import json
import re

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.db import IntegrityError

from haystack.query import SearchQuerySet

from .util import otp_generator, send_otp_email, validate_otp
from .models import User, City, Country, Countrylanguage

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

@login_required
def home(request):
    return render(request, "home.html")

@login_required
def search(request):
    query = request.GET.get("query", "").strip()
    result = {"cities": [], "countries": [], "languages": []}
    
    if not query and len(query) < 3:
        return JsonResponse(result)

    city_pks = list(SearchQuerySet().autocomplete(i_city_name=query).values_list("pk", flat=True))
    country_pks = list(SearchQuerySet().autocomplete(i_country_name=query).values_list("pk", flat=True))
    language_pks = list(SearchQuerySet().autocomplete(i_language_name=query).values_list("pk", flat=True))

    result["cities"] = [ City.objects.filter(pk=city_pk).values().first() for city_pk in city_pks ]
    result["countries"] = [ Country.objects.filter(pk=country_pk).values().first() for country_pk in country_pks ]
    result["languages"] = [ Countrylanguage.objects.filter(pk=language_pk).values().first() for language_pk in language_pks ]

    return render(request, "search_results.html", result)

def signup(request):
    return render(request, "signup.html")

@csrf_exempt
def signup_validate(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"success": False, "message": "invalid request"})

    email = body.get("email", "").strip()
    first_name = body.get("first_name", "").strip()
    last_name = body.get("last_name", "").strip()
    gender = body.get("gender", "female")
    phone_number = body.get("phone_number", "").strip()

    if not email or not EMAIL_REGEX.match(email):
        return JsonResponse({"success": False, "message": "valid email required"})

    if not first_name:
        return JsonResponse({"success": False, "message": "first name required"})

    # Send OTP first — only create user if email is reachable
    otp = otp_generator()
    otp_status = send_otp_email(email, otp)
    if not otp_status:
        return JsonResponse({"success": False, "message": "could not send OTP — check email address"})

    try:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number if phone_number else "",
            gender=gender
        )
        user.full_clean(exclude=['password', 'last_login', 'username'])
        user.save()
    except ValidationError as e:
        # Flatten error messages for the response
        messages = []
        for field, errs in e.message_dict.items():
            if field == 'phone_number':
                messages.append("Invalid phone number — use international format e.g. +911234567890")
            else:
                messages.extend(errs)
        return JsonResponse({"success": False, "message": " | ".join(messages)})
    except IntegrityError:
        # User already exists — still allow OTP flow for login
        pass

    request.session["auth_otp"] = otp
    request.session["auth_email"] = email
    return JsonResponse({"success": True, "message": "otp sent to email"})

def c_login(request):
    return render(request, "login.html")


@csrf_exempt
def send_otp(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"success": False, "message": "invalid request"})

    email = body.get("email", "").strip()

    if not email or not EMAIL_REGEX.match(email):
        return JsonResponse({"success": False, "message": "valid email address required"})

    otp = otp_generator()
    otp_status = send_otp_email(email, otp)
    if not otp_status:
        return JsonResponse({"success": False, "message": "could not send OTP — check email address"})

    request.session["auth_otp"] = otp
    request.session["auth_email"] = email
    return JsonResponse({"success": True, "message": "otp sent"})

@csrf_exempt
def login_validate(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"success": False, "message": "invalid request"})

    sent_otp = request.session.get("auth_otp", "")
    sent_email = request.session.get("auth_email", "")
    email = body.get("email", "").strip()
    otp = body.get("otp", "").strip()

    result = validate_otp(otp, sent_otp, email, sent_email)
    
    if not result["success"]:
        return JsonResponse(result)

    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        result = {"success": False, "message": "please signup"}
        return JsonResponse(result)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    result = {"success": True, "message": "login succeeded"}
    return JsonResponse(result)

@login_required
def c_logout(request):
    logout(request)
    return HttpResponseRedirect("/login")

@login_required
def get_country_details(request, country_name):
    country = Country.objects.get(name=country_name)
    result = {"country": country}
    
    return render(request, "country.html", result)


def health(request):
    """Public health check endpoint — no authentication required."""
    return JsonResponse({"status": "UP"})

