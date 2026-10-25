import pytest
from allauth.account.internal.flows.email_verification_by_code import (
    EMAIL_VERIFICATION_CODE_SESSION_KEY,
)
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

PASSWORD = "A-valid-password-2026"
pytestmark = pytest.mark.django_db


@pytest.fixture
def verified_member():
    user = get_user_model().objects.create_user(
        username="template_member",
        email="template-member@example.net",
        password=PASSWORD,
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        primary=True,
        verified=True,
    )
    return user


def signup_data(**overrides) -> dict[str, str]:
    data = {
        "username": "template_signup",
        "email": "template-signup@example.net",
        "password1": PASSWORD,
        "password2": PASSWORD,
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize(
    "url_name, heading",
    [
        ("account_signup", "Join the Club"),
        ("account_login", "Log in"),
        ("account_request_login_code", "Request a sign-in code"),
        ("account_reset_password", "Reset your password"),
        ("account_inactive", "Account inactive"),
    ],
)
def test_public_authentication_pages_use_global_shell(client, url_name, heading):
    response = client.get(reverse(url_name))

    assert response.status_code == 200
    content = response.content.decode()
    assert "<h1" in content
    assert heading in content
    assert 'href="/static/css/site.css"' in content
    assert 'src="/static/vendor/alpine/alpine.min.js"' in content
    assert '<header class="site-header">' in content
    assert '<footer class="site-footer">' in content


def test_member_authentication_pages_use_global_shell(client, verified_member):
    client.force_login(verified_member)

    for url_name, heading in (
        ("account_change_password", "Change password"),
        ("account_logout", "Log out"),
    ):
        response = client.get(reverse(url_name))
        assert response.status_code == 200
        content = response.content.decode()
        assert heading in content
        assert content.count("<h1") == 1
        assert 'id="main-content"' in content


def test_signup_uses_alpine_with_visible_no_javascript_fallback(client):
    response = client.get(reverse("account_signup"))

    content = response.content.decode()
    assert 'x-data="{ isUsyd: false }"' in content
    assert 'x-model="isUsyd"' in content
    assert 'x-ref="usuId"' in content
    assert 'x-show="isUsyd || false"' in content
    assert "x-cloak" not in content
    assert 'name="usu_id"' in content


def test_signup_field_error_is_associated_with_input(client):
    response = client.post(
        reverse("account_signup"),
        signup_data(usu_id="12345678"),
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert 'id="id_usu_id_error"' in content
    assert 'aria-invalid="true"' in content
    assert 'aria-describedby="id_usu_id_error"' in content
    assert "USU ID is only available to USYD students." in content


def test_login_non_field_error_has_focus_target_and_hides_password(client):
    submitted_password = "Never-render-this-password-2026"

    response = client.post(
        reverse("account_login"),
        {"login": "missing-user", "password": submitted_password},
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert 'role="alert" tabindex="-1" data-error-summary' in content
    assert submitted_password not in content
    assert "The username and/or password you specified are not correct." in content


def test_verification_code_input_is_mobile_friendly_and_never_echoed(client):
    client.post(reverse("account_signup"), signup_data())
    actual_code = client.session[EMAIL_VERIFICATION_CODE_SESSION_KEY]["code"]
    assert actual_code.isdigit()

    get_response = client.get(reverse("account_email_verification_sent"))
    get_content = get_response.content.decode()
    assert get_response.status_code == 200
    assert 'autocomplete="one-time-code"' in get_content
    assert 'inputmode="numeric"' in get_content
    assert 'pattern="[0-9]*"' in get_content
    assert actual_code not in get_content

    submitted_code = "000000000" if actual_code != "000000000" else "111111111"
    invalid_response = client.post(
        reverse("account_email_verification_sent"),
        {"code": submitted_code, "action": "verify"},
    )
    invalid_content = invalid_response.content.decode()
    assert invalid_response.status_code == 200
    assert f'value="{submitted_code}"' not in invalid_content
    assert 'id="id_code_error"' in invalid_content
    assert 'aria-describedby="id_code_error"' in invalid_content


def test_code_generation_is_numeric_for_mobile_keyboards():
    assert settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_FORMAT == {
        "numeric": True,
        "dashed": False,
    }
    assert settings.ACCOUNT_LOGIN_BY_CODE_FORMAT == {
        "numeric": True,
        "dashed": False,
    }


def test_account_alpine_markup_preserves_server_side_form(
    client,
    verified_member,
):
    client.force_login(verified_member)

    response = client.get(reverse("account"))

    content = response.content.decode()
    assert 'x-data="{ isUsyd: false }"' in content
    assert 'x-model="isUsyd"' in content
    assert 'x-ref="usuId"' in content
    assert 'x-show="isUsyd || false"' in content
    assert "<form" in content
    assert 'method="post"' in content


def test_invalid_password_change_does_not_echo_passwords(client, verified_member):
    client.force_login(verified_member)
    current_password = "Wrong-current-password-2026"
    new_password = "Another-valid-password-2026"

    response = client.post(
        reverse("account_change_password"),
        {
            "oldpassword": current_password,
            "password1": new_password,
            "password2": new_password,
        },
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert current_password not in content
    assert new_password not in content
    assert 'aria-invalid="true"' in content
