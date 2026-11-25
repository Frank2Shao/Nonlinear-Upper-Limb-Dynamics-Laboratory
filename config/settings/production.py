"""Production settings loaded entirely from managed environment variables."""

from .base import *

SECRET_KEY = required_env("DJANGO_SECRET_KEY")

DEBUG = False
RISK_NOTICE_DRAFT_VISIBLE = False

# A new dict, not an update: base.STORAGES is shared with every other settings
# module imported into the same process (as in the settings tests).
STORAGES = {
    **STORAGES,
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
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
EMAIL_TIMEOUT = 10
# Gmail only sends as the account itself, so error emails use the same address.
SERVER_EMAIL = DEFAULT_FROM_EMAIL
# Recipients of server error emails. `check --deploy` warns while it is empty
# (apps/core/checks.py).
ADMINS = [(address, address) for address in optional_csv_env("DJANGO_ADMINS")]

# Avatars live on a persistent volume mounted here and are served by Caddy.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

SECURE_SSL_REDIRECT = True
# Caddy terminates HTTPS and sets X-Forwarded-Proto; gunicorn is reachable only
# from Caddy, so the header cannot be forged by clients.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Caddy replaces X-Forwarded-For, so its single address is the real client.
ALLAUTH_TRUSTED_PROXY_COUNT = 1
# The container health check calls this over plain HTTP from inside the server.
SECURE_REDIRECT_EXEMPT = [r"^health/$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# Logs and error emails share one allow-listed summary (see
# apps/core/error_reporting.py). Requests with a disallowed Host are logged
# but never emailed.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "formatters": {
        "plain": {"()": "apps.core.error_reporting.SafeFormatter"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "plain"},
        "mail_admins": {
            "class": "apps.core.error_reporting.SafeAdminEmailHandler",
            "level": "ERROR",
            "filters": ["require_debug_false"],
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {
            "handlers": ["console", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
