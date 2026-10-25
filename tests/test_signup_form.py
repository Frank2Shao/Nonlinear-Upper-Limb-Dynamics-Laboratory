import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from apps.accounts.forms import SignupForm

User = get_user_model()
pytestmark = pytest.mark.django_db

VALID_SIGNUP_DATA = {
    "username": "new_member",
    "email": "member@example.net",
    "password1": "A-valid-password-2026",
    "password2": "A-valid-password-2026",
}


def signup_data(**overrides):
    return VALID_SIGNUP_DATA | overrides


def test_signup_form_has_design_document_field_order_and_required_fields():
    form = SignupForm()

    assert list(form.fields) == [
        "username",
        "email",
        "password1",
        "password2",
        "is_usyd_student",
        "usu_id",
    ]
    assert form.fields["username"].required is True
    assert form.fields["email"].required is True
    assert form.fields["password1"].required is True
    assert form.fields["password2"].required is True
    assert form.fields["is_usyd_student"].required is False
    assert form.fields["usu_id"].required is False


@pytest.mark.parametrize("field", ["username", "email", "password1", "password2"])
def test_signup_form_rejects_missing_required_field(field):
    data = signup_data()
    data.pop(field)

    form = SignupForm(data=data)

    assert not form.is_valid()
    assert "required" in form.errors[field][0].lower()


def test_signup_form_accepts_any_valid_email_domain():
    form = SignupForm(data=signup_data(email="member@community.example"))

    assert form.is_valid(), form.errors


def test_signup_form_rejects_duplicate_username():
    User.objects.create_user(
        username="existing_member",
        email="existing@example.net",
        password="A-valid-password-2026",
    )
    form = SignupForm(data=signup_data(username="existing_member"))

    assert not form.is_valid()
    assert "username" in form.errors


def test_signup_form_accepts_non_usyd_member_without_usu_id():
    form = SignupForm(data=signup_data())

    assert form.is_valid(), form.errors
    assert form.cleaned_data["is_usyd_student"] is False
    assert form.cleaned_data["usu_id"] is None


def test_signup_form_rejects_usu_id_bypass_for_non_usyd_member():
    form = SignupForm(data=signup_data(usu_id="00123456"))

    assert not form.is_valid()
    assert form.errors["usu_id"] == ["USU ID is only available to USYD students."]


def test_signup_form_accepts_usyd_member_without_usu_id():
    form = SignupForm(data=signup_data(is_usyd_student="on"))

    assert form.is_valid(), form.errors
    assert form.cleaned_data["is_usyd_student"] is True
    assert form.cleaned_data["usu_id"] is None


def test_signup_form_normalizes_numeric_usu_id_for_usyd_member():
    form = SignupForm(data=signup_data(is_usyd_student="on", usu_id=" 00123456 "))

    assert form.is_valid(), form.errors
    assert form.cleaned_data["usu_id"] == "00123456"


def test_signup_form_rejects_non_numeric_usu_id():
    form = SignupForm(data=signup_data(is_usyd_student="on", usu_id="123A456"))

    assert not form.is_valid()
    assert form.errors["usu_id"] == ["USU ID must contain digits only."]


def test_plain_http_signup_creates_non_usyd_user_and_redirects_to_verification(
    client,
):
    response = client.post(
        reverse("account_signup"),
        data=signup_data(email="plain-member@example.net"),
    )

    user = User.objects.get(username="new_member")
    assert response.status_code == 302
    assert response.url == reverse("account_email_verification_sent")
    assert user.email == "plain-member@example.net"
    assert user.is_usyd_student is False
    assert user.usu_id is None
    assert EmailAddress.objects.filter(
        user=user,
        email="plain-member@example.net",
        verified=False,
    ).exists()
    assert len(mail.outbox) == 1


def test_plain_http_signup_saves_usyd_identity_and_pending_usu_id(client):
    response = client.post(
        reverse("account_signup"),
        data=signup_data(
            username="usyd_member",
            email="student@example.org",
            is_usyd_student="on",
            usu_id="00123456",
        ),
    )

    user = User.objects.get(username="usyd_member")
    assert response.status_code == 302
    assert response.url == reverse("account_email_verification_sent")
    assert user.is_usyd_student is True
    assert user.usu_id == "00123456"
    assert user.usu_review_status == User.UsuReviewStatus.PENDING


def test_duplicate_email_preserves_enumeration_protection(client):
    existing_user = User.objects.create_user(
        username="existing_member",
        email="member@example.net",
        password="A-valid-password-2026",
    )
    EmailAddress.objects.create(
        user=existing_user,
        email=existing_user.email,
        primary=True,
        verified=True,
    )

    response = client.post(
        reverse("account_signup"),
        data=signup_data(username="different_username"),
    )

    assert response.status_code == 302
    assert response.url == reverse("account_email_verification_sent")
    assert User.objects.count() == 1
    assert not User.objects.filter(username="different_username").exists()
    assert len(mail.outbox) == 1
