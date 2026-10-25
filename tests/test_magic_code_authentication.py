import logging
import time

import pytest
from allauth.account.internal.stagekit import LOGIN_SESSION_KEY
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.urls import reverse

User = get_user_model()
PASSWORD = "A-valid-password-2026"
pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_allauth_rate_limits():
    cache.clear()


def create_user(
    *,
    username: str,
    email: str,
    verified: bool = True,
    is_active: bool = True,
):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=PASSWORD,
        is_active=is_active,
    )
    email_address = EmailAddress.objects.create(
        user=user,
        email=email,
        primary=True,
        verified=verified,
    )
    return user, email_address


def request_login_code(client, *, email: str, next_url: str | None = None):
    url = reverse("account_request_login_code")
    if next_url is not None:
        url = f"{url}?next={next_url}"
    return client.post(url, data={"email": email})


def login_code_state(client) -> dict[str, object]:
    return client.session[LOGIN_SESSION_KEY]["state"]["stages"]["login_by_code"]["data"]


def test_valid_magic_code_logs_in_verified_user_and_preserves_safe_target(client):
    user, _ = create_user(
        username="magic_member",
        email="magic-member@example.net",
    )
    target = "/members/private/"
    request_response = request_login_code(
        client,
        email=user.email,
        next_url=target,
    )
    code = login_code_state(client)["code"]

    confirm_response = client.post(
        f"{reverse('account_confirm_login_code')}?next={target}",
        data={"code": code},
    )

    assert request_response.status_code == 302
    assert request_response.url == (
        f"{reverse('account_confirm_login_code')}?next=%2Fmembers%2Fprivate%2F"
    )
    assert len(mail.outbox) == 1
    assert confirm_response.status_code == 302
    assert confirm_response.url == target
    assert client.session["_auth_user_id"] == str(user.pk)
    assert LOGIN_SESSION_KEY not in client.session


def test_incorrect_magic_code_keeps_user_logged_out(client):
    user, _ = create_user(
        username="wrong_magic_code",
        email="wrong-magic-code@example.net",
    )
    request_login_code(client, email=user.email)

    response = client.post(
        reverse("account_confirm_login_code"),
        data={"code": "WRONG-CODE"},
    )

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session
    assert login_code_state(client)["failed_attempts"] == 1


def test_magic_code_attempt_limit_aborts_login_process(client):
    user, _ = create_user(
        username="magic_attempt_limit",
        email="magic-attempt-limit@example.net",
    )
    request_login_code(client, email=user.email)

    for _ in range(settings.ACCOUNT_LOGIN_BY_CODE_MAX_ATTEMPTS - 1):
        response = client.post(
            reverse("account_confirm_login_code"),
            data={"code": "WRONG-CODE"},
        )
        assert response.status_code == 200

    final_response = client.post(
        reverse("account_confirm_login_code"),
        data={"code": "WRONG-CODE"},
    )

    assert final_response.status_code == 302
    assert final_response.url == reverse("account_request_login_code")
    assert "_auth_user_id" not in client.session
    assert LOGIN_SESSION_KEY not in client.session


def test_expired_magic_code_cannot_log_user_in(client):
    user, _ = create_user(
        username="expired_magic_code",
        email="expired-magic-code@example.net",
    )
    request_login_code(client, email=user.email)
    session = client.session
    login_state = session[LOGIN_SESSION_KEY]
    login_state["state"]["stages"]["login_by_code"]["data"]["at"] = (
        time.time() - settings.ACCOUNT_LOGIN_BY_CODE_TIMEOUT - 1
    )
    session[LOGIN_SESSION_KEY] = login_state
    session.save()

    response = client.post(
        reverse("account_confirm_login_code"),
        data={"code": login_code_state(client)["code"]},
    )

    assert response.status_code == 302
    assert response.url == reverse("account_request_login_code")
    assert "_auth_user_id" not in client.session
    assert LOGIN_SESSION_KEY not in client.session


def test_magic_code_cannot_be_reused(client):
    user, _ = create_user(
        username="single_use_magic_code",
        email="single-use-magic-code@example.net",
    )
    request_login_code(client, email=user.email)
    code = login_code_state(client)["code"]
    first_response = client.post(
        reverse("account_confirm_login_code"),
        data={"code": code},
    )

    second_response = client.post(
        reverse("account_confirm_login_code"),
        data={"code": code},
    )

    assert first_response.status_code == 302
    assert second_response.status_code == 302
    assert second_response.url == settings.LOGIN_REDIRECT_URL


def test_magic_code_can_be_resent_twice_then_resend_is_unavailable(client):
    user, _ = create_user(
        username="resend_magic_code",
        email="resend-magic-code@example.net",
    )
    request_login_code(client, email=user.email)
    codes = [login_code_state(client)["code"]]

    for expected_count in (1, 2):
        response = client.post(
            reverse("account_confirm_login_code"),
            data={"action": "resend"},
        )
        state = login_code_state(client)
        codes.append(state["code"])
        assert response.status_code == 302
        assert response.url == reverse("account_confirm_login_code")
        assert state["resend_count"] == expected_count

    response = client.post(
        reverse("account_confirm_login_code"),
        data={"action": "resend"},
    )

    assert len(set(codes)) == 3
    assert len(mail.outbox) == 3
    assert response.status_code == 200
    assert login_code_state(client)["resend_count"] == 2
    assert len(mail.outbox) == 3


def test_login_code_request_rate_limit_applies_per_email(client):
    user, _ = create_user(
        username="magic_request_limit",
        email="magic-request-limit@example.net",
    )

    for _ in range(3):
        response = request_login_code(client, email=user.email)
        assert response.status_code == 302
        client.session.flush()

    limited_response = request_login_code(client, email=user.email)

    assert limited_response.status_code == 200
    assert "Too many failed login attempts" in limited_response.content.decode()
    assert len(mail.outbox) == 3
    assert "_auth_user_id" not in client.session


@pytest.mark.parametrize(
    ("username", "email", "verified", "is_active"),
    [
        ("unverified_magic", "unverified-magic@example.net", False, True),
        ("inactive_magic", "inactive-magic@example.net", True, False),
    ],
)
def test_ineligible_account_cannot_receive_a_working_magic_code(
    client,
    username,
    email,
    verified,
    is_active,
):
    _, email_address = create_user(
        username=username,
        email=email,
        verified=verified,
        is_active=is_active,
    )

    request_response = request_login_code(client, email=email)
    state = login_code_state(client)
    confirm_response = client.post(
        reverse("account_confirm_login_code"),
        data={"code": "123456"},
    )

    email_address.refresh_from_db()
    assert request_response.status_code == 302
    assert request_response.url == reverse("account_confirm_login_code")
    assert "code" not in state
    assert confirm_response.status_code == 200
    assert "_auth_user_id" not in client.session
    assert email_address.verified is verified
    assert len(mail.outbox) == 1
    assert client.session[LOGIN_SESSION_KEY]["user_pk"] is None


def test_magic_code_request_does_not_reveal_email_existence(client):
    user, _ = create_user(
        username="enumeration_magic",
        email="enumeration-magic@example.net",
    )
    known_response = request_login_code(client, email=user.email)
    known_url = known_response.url
    known_status = known_response.status_code
    client.session.flush()
    cache.clear()

    unknown_response = request_login_code(
        client,
        email="unknown-magic@example.net",
    )

    assert known_status == unknown_response.status_code == 302
    assert known_url == unknown_response.url == reverse("account_confirm_login_code")
    assert len(mail.outbox) == 2
    assert "code" not in login_code_state(client)
    assert "_auth_user_id" not in client.session


def test_password_login_does_not_require_magic_code(client):
    user, _ = create_user(
        username="password_without_magic",
        email="password-without-magic@example.net",
    )

    response = client.post(
        reverse("account_login"),
        data={"login": user.username, "password": PASSWORD},
    )

    assert response.status_code == 302
    assert response.url == settings.LOGIN_REDIRECT_URL
    assert client.session["_auth_user_id"] == str(user.pk)
    assert len(mail.outbox) == 0


def test_magic_code_logs_do_not_contain_code_or_complete_email(client, caplog):
    email = "private-magic@example.net"
    user, _ = create_user(username="private_magic", email=email)
    caplog.set_level(logging.DEBUG)
    request_login_code(client, email=user.email)
    code = login_code_state(client)["code"]

    response = client.post(
        reverse("account_confirm_login_code"),
        data={"code": code},
    )

    assert response.status_code == 302
    assert code not in caplog.text
    assert email not in caplog.text
