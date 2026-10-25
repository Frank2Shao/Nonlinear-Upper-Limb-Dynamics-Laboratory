import re
import socket
import subprocess
from pathlib import Path

import pytest
from allauth.account.internal.flows.email_verification_by_code import (
    EMAIL_VERIFICATION_CODE_SESSION_KEY,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.services import update_usu_identity

User = get_user_model()
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PASSWORD = "A-valid-password-2026"
FORBIDDEN_FILE_NAMES = {".env", "db.sqlite3"}
FORBIDDEN_SUFFIXES = {".key", ".p12", ".pem", ".pfx", ".sqlite", ".sqlite3"}
SECRET_PATTERNS = {
    "private key": re.compile(rb"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"),
    "AWS access key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "GitHub token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
    "Slack token": re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
    "Stripe live key": re.compile(rb"sk_live_[A-Za-z0-9]{16,}"),
}


def repository_files() -> list[Path]:
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=True,
    )
    return [
        PROJECT_ROOT / Path(path.decode("utf-8"))
        for path in result.stdout.split(b"\0")
        if path
    ]


def test_repository_contains_no_secret_files_or_high_confidence_credentials():
    violations = []
    for path in repository_files():
        relative_path = path.relative_to(PROJECT_ROOT)
        if (
            path.name in FORBIDDEN_FILE_NAMES
            or path.suffix.lower() in FORBIDDEN_SUFFIXES
        ):
            violations.append(f"forbidden file: {relative_path}")
            continue
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        content = path.read_bytes()
        if b"\0" in content:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                violations.append(f"{label}: {relative_path}")

    assert violations == []


def test_test_suite_blocks_external_network_access():
    with pytest.raises(
        RuntimeError, match="External (?:DNS|network) access is blocked"
    ):
        socket.getaddrinfo("example.com", 443)


@pytest.mark.django_db
def test_authentication_and_identity_secrets_are_not_logged(client, caplog):
    email = "log-private@example.net"
    username = "log_private"
    usu_id = "45678901"
    response = client.post(
        reverse("account_signup"),
        data={
            "username": username,
            "email": email,
            "password1": PASSWORD,
            "password2": PASSWORD,
            "is_usyd_student": "on",
            "usu_id": usu_id,
        },
    )
    assert response.status_code == 302
    code = client.session[EMAIL_VERIFICATION_CODE_SESSION_KEY]["code"]
    session_key = client.session.session_key

    client.post(
        reverse("account_email_verification_sent"),
        data={"code": code},
    )

    logged_output = caplog.text
    for sensitive_value in (PASSWORD, code, email, usu_id, session_key):
        assert sensitive_value not in logged_output


@pytest.mark.django_db
def test_public_pages_do_not_expose_private_identity_fields(client):
    user = User.objects.create_user(
        username="private_member",
        email="private-member@example.net",
        password=PASSWORD,
    )
    update_usu_identity(
        user=user,
        is_usyd_student=True,
        usu_id="56789012",
    )
    user.refresh_from_db()
    private_values = (
        user.email,
        user.usu_id,
        User.UsuReviewStatus.PENDING,
    )

    for url_name in (
        "home",
        "account_login",
        "account_signup",
        "account_request_login_code",
        "account_reset_password",
    ):
        response = client.get(reverse(url_name))
        assert response.status_code == 200
        content = response.content.decode()
        for private_value in private_values:
            assert private_value not in content


def test_security_settings_keep_session_cookie_http_only():
    assert settings.SESSION_COOKIE_HTTPONLY is True
