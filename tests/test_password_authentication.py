import re

import pytest
from allauth.account.internal.flows.email_verification_by_code import (
    EMAIL_VERIFICATION_CODE_SESSION_KEY,
)
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.urls import reverse

from apps.members.models import MemberProfile

User = get_user_model()
PASSWORD = "A-valid-password-2026"
NEW_PASSWORD = "A-different-valid-password-2026"
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
    EmailAddress.objects.create(
        user=user,
        email=email,
        primary=True,
        verified=verified,
    )
    return user


def login(client, *, username: str, password: str, next_url: str | None = None):
    url = reverse("account_login")
    if next_url is not None:
        url = f"{url}?next={next_url}"
    return client.post(url, data={"login": username, "password": password})


def login_errors(response) -> tuple[str, ...]:
    return tuple(str(error) for error in response.context["form"].non_field_errors())


def test_verified_user_can_log_in_and_is_redirected_to_account(client):
    user = create_user(username="verified_login", email="verified-login@example.net")

    response = login(client, username=user.username, password=PASSWORD)

    assert response.status_code == 302
    assert response.url == settings.LOGIN_REDIRECT_URL
    assert client.session["_auth_user_id"] == str(user.pk)


def test_login_returns_to_safe_original_target(client):
    user = create_user(username="safe_redirect", email="safe-redirect@example.net")
    target = "/members/private/?tab=profile"

    response = login(
        client,
        username=user.username,
        password=PASSWORD,
        next_url=target,
    )

    assert response.status_code == 302
    assert response.url == target
    assert client.session["_auth_user_id"] == str(user.pk)


def test_login_rejects_external_redirect_target(client):
    user = create_user(username="unsafe_redirect", email="unsafe-redirect@example.net")

    response = login(
        client,
        username=user.username,
        password=PASSWORD,
        next_url="https://attacker.example/collect-session",
    )

    assert response.status_code == 302
    assert response.url == settings.LOGIN_REDIRECT_URL
    assert client.session["_auth_user_id"] == str(user.pk)


def test_unknown_username_and_wrong_password_use_the_same_generic_error(client):
    user = create_user(username="generic_error", email="generic-error@example.net")

    unknown_response = login(
        client,
        username="unknown_account",
        password=PASSWORD,
    )
    wrong_password_response = login(
        client,
        username=user.username,
        password="Incorrect-password-2026",
    )

    assert unknown_response.status_code == 200
    assert wrong_password_response.status_code == 200
    assert login_errors(unknown_response) == login_errors(wrong_password_response)
    assert login_errors(unknown_response) == (
        "The username and/or password you specified are not correct.",
    )
    assert "_auth_user_id" not in client.session


def test_unverified_user_resumes_verification_before_login(client):
    user = create_user(
        username="pending_login",
        email="pending-login@example.net",
        verified=False,
    )
    target = "/members/private/"

    login_response = login(
        client,
        username=user.username,
        password=PASSWORD,
        next_url=target,
    )

    assert login_response.status_code == 302
    assert login_response.url == reverse("account_email_verification_sent")
    assert "_auth_user_id" not in client.session
    assert EMAIL_VERIFICATION_CODE_SESSION_KEY in client.session
    assert len(mail.outbox) == 1
    assert not MemberProfile.objects.filter(user=user).exists()

    code = client.session[EMAIL_VERIFICATION_CODE_SESSION_KEY]["code"]
    verification_response = client.post(
        reverse("account_email_verification_sent"),
        data={"code": code},
    )

    assert verification_response.status_code == 302
    assert verification_response.url == target
    assert client.session["_auth_user_id"] == str(user.pk)
    assert MemberProfile.objects.filter(user=user).count() == 1


def test_inactive_account_is_refused_without_an_authenticated_session(client):
    user = create_user(
        username="inactive_login",
        email="inactive-login@example.net",
        is_active=False,
    )

    response = login(client, username=user.username, password=PASSWORD)

    assert response.status_code == 302
    assert response.url == reverse("account_inactive")
    assert "_auth_user_id" not in client.session


def test_password_reset_request_does_not_reveal_email_existence(client):
    user = create_user(username="reset_member", email="reset-member@example.net")
    reset_url = reverse("account_reset_password")

    known_response = client.post(reset_url, data={"email": user.email})
    known_message_count = len(mail.outbox)
    unknown_response = client.post(
        reset_url,
        data={"email": "unknown-reset@example.net"},
    )

    assert known_response.status_code == 302
    assert unknown_response.status_code == 302
    assert known_response.url == reverse("account_reset_password_done")
    assert unknown_response.url == known_response.url
    assert known_message_count == 1
    assert len(mail.outbox) == 2
    assert "_auth_user_id" not in client.session


def test_password_reset_link_changes_password(client):
    user = create_user(
        username="complete_reset",
        email="complete-reset@example.net",
    )
    request_response = client.post(
        reverse("account_reset_password"),
        data={"email": user.email},
    )
    reset_url_match = re.search(
        r"http://testserver(/accounts/password/reset/key/[^\s]+)",
        mail.outbox[0].body,
    )

    assert request_response.status_code == 302
    assert reset_url_match is not None

    token_response = client.get(reset_url_match.group(1))

    assert token_response.status_code == 302
    assert token_response.url.endswith("-set-password/")

    reset_response = client.post(
        token_response.url,
        data={"password1": NEW_PASSWORD, "password2": NEW_PASSWORD},
    )

    user.refresh_from_db()
    assert reset_response.status_code == 302
    assert reset_response.url == reverse("account_reset_password_from_key_done")
    assert user.check_password(NEW_PASSWORD)
    assert not user.check_password(PASSWORD)
    assert "_auth_user_id" not in client.session


def test_get_logout_does_not_end_session_but_post_logout_does(client):
    user = create_user(username="logout_member", email="logout-member@example.net")
    login_response = login(client, username=user.username, password=PASSWORD)

    get_response = client.get(reverse("account_logout"))

    assert login_response.status_code == 302
    assert get_response.status_code == 200
    assert client.session["_auth_user_id"] == str(user.pk)

    post_response = client.post(reverse("account_logout"))

    assert post_response.status_code == 302
    assert post_response.url == settings.LOGOUT_REDIRECT_URL
    assert "_auth_user_id" not in client.session
