"""Local development settings."""

from .base import *

SECRET_KEY = required_env("DJANGO_SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = required_csv_env("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = required_csv_env("DJANGO_CSRF_TRUSTED_ORIGINS")

DATABASES = {"default": database_from_url(required_env("DATABASE_URL"))}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
