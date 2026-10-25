import logging
import time

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
pytestmark = pytest.mark.django_db


def signup_data(*, username: str, email: str) -> dict[str, str]:
    return {
        "username": username,
        "email": email,
        "password1": "A-valid-password-2026",
        "password2": "A-valid-password-2026",
    }


def start_verification(client, *, username: str, email: str):
    response = client.post(
        reverse("account_signup"),
        data=signup_data(username=username, email=email),
    )
    state = client.session[EMAIL_VERIFICATION_CODE_SESSION_KEY]
    user = User.objects.get(username=username)
    email_address = EmailAddress.objects.get(user=user, email=email)

    assert response.status_code == 302
    assert response.url == reverse("account_email_verification_sent")
    return user, email_address, state["code"]


def test_pending_user_is_not_authenticated_or_a_member(client):
    user, email_address, _ = start_verification(
        client,
        username="pending_member",
        email="pending@example.net",
    )

    assert email_address.verified is False
    assert not MemberProfile.objects.filter(user=user).exists()
    assert "_auth_user_id" not in client.session


def test_correct_code_verifies_email_logs_in_and_creates_hidden_profile(client):
    user, email_address, code = start_verification(
        client,
        username="verified_member",
        email="verified@example.net",
    )

    response = client.post(
        reverse("account_email_verification_sent"),
        data={"code": code},
    )

    email_address.refresh_from_db()
    profile = MemberProfile.objects.get(user=user)
    assert response.status_code == 302
    assert response.url == settings.LOGIN_REDIRECT_URL
    assert email_address.verified is True
    assert client.session["_auth_user_id"] == str(user.pk)
    assert profile.is_published is False
    assert profile.is_hidden_by_admin is False
    assert EMAIL_VERIFICATION_CODE_SESSION_KEY not in client.session


def test_incorrect_code_keeps_account_pending(client):
    user, email_address, _ = start_verification(
        client,
        username="incorrect_code_member",
        email="incorrect-code@example.net",
    )

    response = client.post(
        reverse("account_email_verification_sent"),
        data={"code": "WRONG-CODE"},
    )

    email_address.refresh_from_db()
    assert response.status_code == 200
    assert email_address.verified is False
    assert not MemberProfile.objects.filter(user=user).exists()
    assert "_auth_user_id" not in client.session
    assert EMAIL_VERIFICATION_CODE_SESSION_KEY in client.session


def test_expired_code_clears_pending_process_and_redirects_to_login(client):
    user, email_address, code = start_verification(
        client,
        username="expired_code_member",
        email="expired-code@example.net",
    )
    session = client.session
    state = session[EMAIL_VERIFICATION_CODE_SESSION_KEY]
    state["at"] = time.time() - settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_TIMEOUT - 1
    session[EMAIL_VERIFICATION_CODE_SESSION_KEY] = state
    session.save()

    response = client.post(
        reverse("account_email_verification_sent"),
        data={"code": code},
    )

    email_address.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse("account_login")
    assert email_address.verified is False
    assert not MemberProfile.objects.filter(user=user).exists()
    assert EMAIL_VERIFICATION_CODE_SESSION_KEY not in client.session


def test_verification_code_cannot_be_reused_or_create_duplicate_profile(client):
    user, _, code = start_verification(
        client,
        username="single_use_member",
        email="single-use@example.net",
    )
    first_response = client.post(
        reverse("account_email_verification_sent"),
        data={"code": code},
    )

    second_response = client.post(
        reverse("account_email_verification_sent"),
        data={"code": code},
    )

    assert first_response.status_code == 302
    assert second_response.status_code == 302
    assert second_response.url == reverse("account_email")
    assert MemberProfile.objects.filter(user=user).count() == 1


def test_resend_replaces_code_and_sends_a_new_email(client):
    user, email_address, first_code = start_verification(
        client,
        username="resend_member",
        email="resend@example.net",
    )
    cache.clear()

    response = client.post(
        reverse("account_email_verification_sent"),
        data={"action": "resend"},
    )

    new_code = client.session[EMAIL_VERIFICATION_CODE_SESSION_KEY]["code"]
    email_address.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse("account_email_verification_sent")
    assert new_code != first_code
    assert len(mail.outbox) == 2
    assert email_address.verified is False
    assert not MemberProfile.objects.filter(user=user).exists()


def test_immediate_resend_is_rate_limited_without_replacing_code(client):
    _, email_address, first_code = start_verification(
        client,
        username="rate_limited_member",
        email="rate-limited@example.net",
    )

    response = client.post(
        reverse("account_email_verification_sent"),
        data={"action": "resend"},
    )

    email_address.refresh_from_db()
    assert response.status_code == 429
    assert client.session[EMAIL_VERIFICATION_CODE_SESSION_KEY]["code"] == first_code
    assert len(mail.outbox) == 1
    assert email_address.verified is False


def test_verification_logs_do_not_contain_code_or_complete_email(client, caplog):
    email = "private-address@example.net"
    caplog.set_level(logging.DEBUG)
    _, _, code = start_verification(
        client,
        username="private_log_member",
        email=email,
    )

    response = client.post(
        reverse("account_email_verification_sent"),
        data={"code": code},
    )

    assert response.status_code == 302
    assert code not in caplog.text
    assert email not in caplog.text
