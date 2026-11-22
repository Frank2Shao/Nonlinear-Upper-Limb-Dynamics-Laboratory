"""Phase 6 Step 46: production runtime settings, health check and error emails."""

import importlib
import json
import os
import subprocess
import sys

import pytest
from django.core import mail
from django.db import OperationalError
from django.test import Client, override_settings
from django.urls import reverse

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


def test_error_reports_use_the_private_filter_everywhere():
    assert PRODUCTION.DEFAULT_EXCEPTION_REPORTER_FILTER == (
        "apps.core.error_reporting.PrivateExceptionReporterFilter"
    )


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


@pytest.mark.django_db
@override_settings(
    ROOT_URLCONF="tests.error_urls",
    ADMINS=[("Admin", "admin@example.invalid")],
)
def test_server_error_email_keeps_the_traceback_and_redacts_member_data():
    member = create_user(
        "error-email-member",
        email="private-member@example.test",
        verified=True,
    )
    client = Client(raise_request_exception=False)
    client.force_login(member)
    session_key = client.session.session_key

    response = client.post(
        "/test-error/500/",
        {
            "email": "private-member@example.test",
            "code": "482913",
            "password": "Private-password-2026",
            "usu_id": "001234567",
        },
    )

    assert response.status_code == 500
    assert len(mail.outbox) == 1
    report = mail.outbox[0]
    text = report.subject + report.body
    assert report.to == ["admin@example.invalid"]
    assert "RuntimeError" in text
    assert "/test-error/500/" in text
    for private in (
        "private-member@example.test",
        "482913",
        "Private-password-2026",
        "001234567",
        session_key,
    ):
        assert private not in text
