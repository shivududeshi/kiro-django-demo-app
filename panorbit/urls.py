"""panorbit URL Configuration

Migrated from django.conf.urls.url() (removed in Django 4.0)
to django.urls.path() / re_path().
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('world.urls')),
]
