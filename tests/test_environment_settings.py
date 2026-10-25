import importlib
import os
import subprocess
import sys


def test_development_settings_use_local_services() -> None:
    settings = importlib.import_module("config.settings.development")

    assert settings.DEBUG is True
    assert settings.DATABASES["default"]["ENGINE"] == ("django.db.backends.postgresql")
    assert settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend"
    assert settings.MEDIA_ROOT == settings.BASE_DIR / "media"


def test_test_settings_are_isolated_from_external_services() -> None:
    settings = importlib.import_module("config.settings.test")

    assert settings.DEBUG is False
    assert settings.DATABASES["default"]["ENGINE"] == ("django.db.backends.postgresql")
    assert (
        settings.DATABASES["default"]["TEST"]["NAME"] == os.environ["POSTGRES_TEST_DB"]
    )
    assert settings.EMAIL_BACKEND == "django.core.mail.backends.locmem.EmailBackend"
    assert settings.PASSWORD_HASHERS == [
        "django.contrib.auth.hashers.MD5PasswordHasher"
    ]


def test_production_settings_enable_security_controls() -> None:
    settings = importlib.import_module("config.settings.production")

    assert settings.DEBUG is False
    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.SECURE_HSTS_SECONDS > 0
    assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert settings.SECURE_HSTS_PRELOAD is True
    assert settings.EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend"
    assert settings.STORAGES["staticfiles"]["BACKEND"] == (
        "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
    )


def test_production_settings_fail_without_secret_key() -> None:
    environment = os.environ.copy()
    environment.pop("DJANGO_SECRET_KEY", None)

    result = subprocess.run(
        [sys.executable, "-c", "import config.settings.production"],
        capture_output=True,
        check=False,
        env=environment,
        text=True,
    )

    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY" in result.stderr
