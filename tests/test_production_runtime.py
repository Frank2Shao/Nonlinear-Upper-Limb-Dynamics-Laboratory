"""Phase 6 Step 46: production runtime settings, health check and error emails."""

import importlib
import json
import logging
import os
import subprocess
import sys

import pytest
from allauth.core.internal.httpkit import get_client_ip
from django.core import mail
from django.db import OperationalError
from django.test import Client, RequestFactory, override_settings
from django.urls import reverse
from django.utils.module_loading import import_string

from apps.core.checks import server_error_recipients
from tests.factories import create_user

PRODUCTION = importlib.import_module("config.settings.production")


def run_production(code: str, **extra_environment: str) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment.update(extra_environment)
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        check=False,
        env=environment,
        text=True,
    )


def test_production_trusts_the_proxy_scheme_and_serves_media_from_a_volume():
    assert PRODUCTION.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    assert PRODUCTION.SECURE_REDIRECT_EXEMPT == [r"^health/$"]
    assert PRODUCTION.MEDIA_URL == "/media/"
    assert PRODUCTION.MEDIA_ROOT == PRODUCTION.BASE_DIR / "media"
    assert PRODUCTION.STATIC_ROOT == PRODUCTION.BASE_DIR / "staticfiles"
    assert PRODUCTION.SERVER_EMAIL == PRODUCTION.DEFAULT_FROM_EMAIL


def test_importing_production_settings_leaves_shared_base_settings_unchanged():
    base = importlib.import_module("config.settings.base")

    assert base.STORAGES["staticfiles"]["BACKEND"] == (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
    assert PRODUCTION.STORAGES["staticfiles"]["BACKEND"] == (
        "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
    )


def test_production_admins_come_from_the_environment():
    result = run_production(
        "import json, config.settings.production as s; print(json.dumps(s.ADMINS))",
        DJANGO_ADMINS=" first@example.invalid, ,second@example.invalid ",
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [
        ["first@example.invalid", "first@example.invalid"],
        ["second@example.invalid", "second@example.invalid"],
    ]


def test_production_logging_is_valid_and_only_emails_request_errors():
    result = run_production(
        "import logging.config, config.settings.production as s;"
        " logging.config.dictConfig(s.LOGGING)"
    )
    loggers = PRODUCTION.LOGGING["loggers"]

    assert result.returncode == 0, result.stderr
    assert PRODUCTION.LOGGING["handlers"]["mail_admins"]["level"] == "ERROR"
    assert [
        name
        for name, config in loggers.items()
        if "mail_admins" in config.get("handlers", [])
    ] == ["django.request"]
    assert "mail_admins" not in loggers["django.security.DisallowedHost"]["handlers"]


@pytest.mark.parametrize(
    ("admins", "expected_ids"),
    ((["admin@example.invalid"], []), ([], ["core.W001"])),
)
def test_deploy_check_warns_until_error_recipients_are_set(admins, expected_ids):
    with override_settings(ADMINS=[(address, address) for address in admins]):
        assert [message.id for message in server_error_recipients(None)] == expected_ids


@pytest.mark.django_db
def test_health_check_reports_ok_without_caching(client):
    response = client.get(reverse("health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "no-cache" in response["Cache-Control"]


@pytest.mark.django_db
def test_health_check_accepts_only_get(client):
    assert client.post(reverse("health")).status_code == 405


@pytest.mark.django_db
def test_health_check_reports_an_unreachable_database_without_details(
    client, monkeypatch, caplog
):
    def unavailable():
        raise OperationalError("connection to server at secret-host failed")

    monkeypatch.setattr("apps.core.views.connection.cursor", unavailable)

    response = client.get(reverse("health"))

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert "secret-host" not in response.content.decode()
    assert "secret-host" not in caplog.text
    assert "database is unavailable" in caplog.text


@pytest.mark.django_db
def test_health_check_is_not_in_the_sitemap(client):
    assert "/health/" not in client.get(reverse("sitemap")).content.decode()


@pytest.mark.django_db
def test_health_answers_plain_http_while_pages_redirect_to_https(client):
    with override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_REDIRECT_EXEMPT=PRODUCTION.SECURE_REDIRECT_EXEMPT,
        SECURE_PROXY_SSL_HEADER=PRODUCTION.SECURE_PROXY_SSL_HEADER,
    ):
        assert client.get(reverse("health")).status_code == 200
        assert client.get(reverse("about")).status_code == 301
        # Behind Caddy the forwarded scheme is HTTPS, so there is no redirect loop.
        forwarded = client.get(reverse("about"), headers={"X-Forwarded-Proto": "https"})
        assert forwarded.status_code == 200


def production_formatter() -> logging.Formatter:
    config = dict(PRODUCTION.LOGGING["formatters"]["plain"])
    factory = config.pop("()", None)
    return import_string(factory)() if factory else logging.Formatter(config["format"])


def production_email_handler() -> logging.Handler:
    return import_string(PRODUCTION.LOGGING["handlers"]["mail_admins"]["class"])()


@pytest.fixture
def failed_request_record(db, caplog):
    """The real django.request record of a failure full of member data."""
    member = create_user(
        "private-username",
        email="private-member@example.test",
        verified=True,
    )
    with override_settings(ROOT_URLCONF="tests.error_urls", ADMINS=[]):
        client = Client(raise_request_exception=False)
        client.force_login(member)
        response = client.post(
            "/test-error/private/RESET-KEY/?email=QUERY-PRIVATE@example.test",
            {"code": "482913", "password": "Private-password-2026"},
            headers={"Referer": "http://testserver/?x=REFERER-PRIVATE"},
            REMOTE_ADDR="203.0.113.9",
        )
        assert response.status_code == 500
    mail.outbox.clear()
    return next(record for record in caplog.records if record.name == "django.request")


PRIVATE_VALUES = (
    "RESET-KEY",
    "QUERY-PRIVATE",
    "REFERER-PRIVATE",
    "MESSAGE-PRIVATE",
    "CHAINED-PRIVATE",
    "private-member@example.test",
    "private-username",
    "482913",
    "Private-password-2026",
    "203.0.113.9",
)


@override_settings(ADMINS=[("Admin", "admin@example.invalid")])
def test_error_email_has_only_types_locations_route_and_status(failed_request_record):
    production_email_handler().handle(failed_request_record)

    report = mail.outbox[0]
    text = report.subject + report.body
    assert report.to == ["admin@example.invalid"]
    for useful in ("RuntimeError", "ValueError", "error_urls.py:", "status=500"):
        assert useful in text
    assert "route=test_private_failure" in text
    assert [value for value in PRIVATE_VALUES if value in text] == []


def test_error_log_has_only_types_locations_route_and_status(failed_request_record):
    text = production_formatter().format(failed_request_record)

    assert "RuntimeError" in text
    assert "route=test_private_failure" in text
    assert [value for value in PRIVATE_VALUES if value in text] == []


@override_settings(ADMINS=[("Admin", "admin@example.invalid")])
def test_repeated_error_is_emailed_once_an_hour(failed_request_record):
    handler = production_email_handler()

    handler.handle(failed_request_record)
    handler.handle(failed_request_record)

    assert len(mail.outbox) == 1


def test_production_logging_never_prints_library_messages_or_arguments():
    result = run_production(
        "import logging.config, config.settings.production as s;"
        " logging.config.dictConfig(s.LOGGING);"
        " logging.getLogger('django.request').warning('Not Found: %s', '/RESET-KEY');"
        " logging.getLogger('gunicorn.error').warning('Invalid PREFORMATTED');"
        " logging.getLogger('apps.example').error('Safe fixed text %s', 'ARG-PRIVATE')"
    )

    assert result.returncode == 0, result.stderr
    assert "Safe fixed text" in result.stderr
    for private in ("RESET-KEY", "PREFORMATTED", "ARG-PRIVATE"):
        assert private not in result.stderr


def test_rate_limits_use_the_client_ip_that_caddy_forwards():
    request = RequestFactory().get(
        "/", REMOTE_ADDR="172.18.0.4", HTTP_X_FORWARDED_FOR="203.0.113.9"
    )

    with override_settings(
        ALLAUTH_TRUSTED_PROXY_COUNT=getattr(
            PRODUCTION, "ALLAUTH_TRUSTED_PROXY_COUNT", 0
        )
    ):
        assert get_client_ip(request) == "203.0.113.9"
