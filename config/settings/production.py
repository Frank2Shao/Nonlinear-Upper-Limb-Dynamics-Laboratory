"""Production settings loaded entirely from managed environment variables."""

from .base import *

SECRET_KEY = required_env("DJANGO_SECRET_KEY")

DEBUG = False

STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
}

ALLOWED_HOSTS = required_csv_env("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = required_csv_env("DJANGO_CSRF_TRUSTED_ORIGINS")

DATABASES = {"default": database_from_url(required_env("DATABASE_URL"))}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = required_env("EMAIL_HOST")
EMAIL_PORT = int(required_env("EMAIL_PORT"))
EMAIL_HOST_USER = required_env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = required_env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = required_bool_env("EMAIL_USE_TLS")
DEFAULT_FROM_EMAIL = required_env("DEFAULT_FROM_EMAIL")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
