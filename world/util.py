import string
import random

from django.core.mail import EmailMessage


def otp_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def send_otp_email(email, otp):
    """Send OTP via email. Uses whatever EMAIL_BACKEND is configured in settings."""
    try:
        message = (
            "Your OTP for Panorbit login is: %s\n\n"
            "This OTP is valid for 10 minutes.\n"
            "If you did not request this, please ignore this email."
        ) % otp
        mail = EmailMessage(
            subject='OTP for Panorbit Login',
            body=message,
            to=[email],
        )
        mail.send()
    except Exception:
        return False
    return True


def validate_otp(otp, sent_otp, email, sent_email):
    if not sent_otp or not sent_email:
        return {"success": False, "message": "session expired"}

    if not email or not otp:
        return {"success": False, "message": "did not receive proper data"}

    if otp != sent_otp:
        return {"success": False, "message": "wrong otp"}

    if email != sent_email:
        return {"success": False, "message": "wrong email"}

    return {"success": True, "message": "validated"}
