import pytest
from allauth.account import app_settings
from django.conf import settings
from django.urls import NoReverseMatch, resolve, reverse


def test_required_authentication_apps_and_backend_are_configured():
    assert "django.contrib.sites" in settings.INSTALLED_APPS
    assert "allauth" in settings.INSTALLED_APPS
    assert "allauth.account" in settings.INSTALLED_APPS
    assert settings.SITE_ID == 1
    assert settings.AUTHENTICATION_BACKENDS == [
        "allauth.account.auth_backends.AuthenticationBackend"
    ]


def test_account_authentication_settings_match_phase_one_scope():
    assert app_settings.LOGIN_METHODS == {app_settings.LoginMethod.USERNAME}
    assert app_settings.SIGNUP_FIELDS == {
        "username": {"required": True},
        "email": {"required": True},
        "password1": {"required": True},
        "password2": {"required": True},
    }
    assert app_settings.UNIQUE_EMAIL is True
    assert app_settings.PREVENT_ENUMERATION is True
    assert app_settings.EMAIL_VERIFICATION == (
        app_settings.EmailVerificationMethod.MANDATORY
    )
    assert app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED is True
    assert app_settings.EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS == 3
    assert app_settings.EMAIL_VERIFICATION_BY_CODE_TIMEOUT == 15 * 60
    assert app_settings.EMAIL_VERIFICATION_MAX_RESEND_COUNT == 2
    assert app_settings.LOGIN_BY_CODE_ENABLED is True
    assert app_settings.LOGIN_BY_CODE_MAX_ATTEMPTS == 3
    assert app_settings.LOGIN_BY_CODE_MAX_RESEND_COUNT == 2
    assert app_settings.LOGIN_BY_CODE_REQUIRED is False
    assert app_settings.LOGIN_BY_CODE_TIMEOUT == 3 * 60
    assert app_settings.PHONE_VERIFICATION_ENABLED is False
    assert app_settings.PASSWORD_RESET_BY_CODE_ENABLED is False
    assert app_settings.LOGOUT_ON_GET is False


def test_redirects_are_reserved_for_later_phase_one_pages():
    assert settings.LOGIN_URL == "account_login"
    assert settings.LOGIN_REDIRECT_URL == "/account/"
    assert settings.LOGOUT_REDIRECT_URL == "/"


def test_default_rate_limits_remain_enabled():
    assert "ACCOUNT_RATE_LIMITS" not in settings._wrapped.__dict__
    assert app_settings.RATE_LIMITS["signup"] == "20/m/ip"
    assert app_settings.RATE_LIMITS["login"] == "30/m/ip"
    assert app_settings.RATE_LIMITS["request_login_code"] == "20/m/ip,3/m/key"
    assert app_settings.RATE_LIMITS["reset_password"] == "20/m/ip,5/m/key"
    assert app_settings.RATE_LIMITS["confirm_email"] == "1/10s/key"


@pytest.mark.parametrize(
    ("url_name", "expected_path"),
    [
        ("account_signup", "/accounts/signup/"),
        ("account_login", "/accounts/login/"),
        ("account_logout", "/accounts/logout/"),
        ("account_email_verification_sent", "/accounts/confirm-email/"),
        ("account_request_login_code", "/accounts/login/code/"),
        ("account_confirm_login_code", "/accounts/login/code/confirm/"),
        ("account_reset_password", "/accounts/password/reset/"),
        ("account_reset_password_done", "/accounts/password/reset/done/"),
        (
            "account_reset_password_from_key_done",
            "/accounts/password/reset/key/done/",
        ),
    ],
)
def test_required_account_urls_are_reversible(url_name, expected_path):
    path = reverse(url_name)

    assert path == expected_path
    assert resolve(path).url_name == url_name


def test_password_reset_confirmation_url_is_reversible():
    path = reverse(
        "account_reset_password_from_key",
        kwargs={"uidb36": "abc123", "key": "test-key"},
    )

    assert path == "/accounts/password/reset/key/abc123-test-key/"
    assert resolve(path).url_name == "account_reset_password_from_key"


@pytest.mark.parametrize(
    "url_name",
    [
        "account_confirm_email",
        "account_verify_phone",
        "account_change_phone",
        "socialaccount_login_cancelled",
        "mfa_login",
    ],
)
def test_excluded_authentication_routes_are_not_available(url_name):
    with pytest.raises(NoReverseMatch):
        reverse(url_name)
