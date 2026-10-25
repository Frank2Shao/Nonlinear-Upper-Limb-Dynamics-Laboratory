"""Automated test settings."""

from .base import *

SECRET_KEY = "test-only-secret-key-not-for-any-deployed-environment"

DEBUG = False

ALLOWED_HOSTS = ["testserver"]

DATABASES = {"default": database_from_url(required_env("DATABASE_URL"))}
DATABASES["default"]["TEST"] = {"NAME": required_env("POSTGRES_TEST_DB")}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
