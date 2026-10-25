import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.accounts.services import review_usu_id

User = get_user_model()
PASSWORD = "A-valid-password-2026"
pytestmark = pytest.mark.django_db


def create_user(*, username: str, verified: bool = True, **extra_fields):
    can_review_usu_id = extra_fields.pop("can_review_usu_id", False)
    email = f"{username}@example.net"
    user = User.objects.create_user(
        username=username,
        email=email,
        password=PASSWORD,
        **extra_fields,
    )
    EmailAddress.objects.create(
        user=user,
        email=email,
        primary=True,
        verified=verified,
    )
    if can_review_usu_id:
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="accounts",
                codename="review_usu_id",
            )
        )
    return user


def test_anonymous_user_is_redirected_to_login(client):
    response = client.get(reverse("account"))

    assert response.status_code == 302
    assert response.url == f"{reverse('account_login')}?next={reverse('account')}"


def test_member_sees_only_their_account_information(client):
    member = create_user(username="account_member")
    other = create_user(username="other_member")
    client.force_login(member)

    response = client.get(reverse("account"))

    assert response.status_code == 200
    content = response.content.decode()
    assert member.username in content
    assert member.email in content
    assert other.username not in content
    assert other.email not in content
    assert "Verified" in content


def test_account_page_reports_unverified_email_status(client):
    member = create_user(username="unverified_status", verified=False)
    client.force_login(member)

    response = client.get(reverse("account"))

    assert response.status_code == 200
    assert "Not verified" in response.content.decode()


def test_account_form_is_initialized_from_the_current_member(client):
    member = create_user(
        username="existing_identity",
        is_usyd_student=True,
        usu_id="00112233",
    )
    client.force_login(member)

    response = client.get(reverse("account"))

    assert response.status_code == 200
    assert response.context["form"].initial == {
        "is_usyd_student": True,
        "usu_id": "00112233",
    }


def test_member_can_submit_numeric_usu_id_and_preserve_leading_zeroes(client):
    member = create_user(username="numeric_account")
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={"is_usyd_student": "on", "usu_id": " 00123456 "},
    )

    assert response.status_code == 302
    assert response.url == reverse("account")
    member.refresh_from_db()
    assert member.is_usyd_student
    assert member.usu_id == "00123456"
    assert member.usu_review_status == User.UsuReviewStatus.PENDING


def test_non_usyd_member_cannot_submit_usu_id(client):
    member = create_user(username="non_usyd_account")
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={"usu_id": "12345678"},
    )

    assert response.status_code == 200
    assert "USU ID is only available to USYD students." in response.content.decode()
    member.refresh_from_db()
    assert not member.is_usyd_student
    assert member.usu_id is None


def test_account_rejects_non_numeric_usu_id(client):
    member = create_user(username="invalid_usu_account")
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={"is_usyd_student": "on", "usu_id": "1234A678"},
    )

    assert response.status_code == 200
    assert "USU ID must contain digits only." in response.content.decode()
    member.refresh_from_db()
    assert member.usu_id is None


def test_changing_reviewed_usu_id_returns_status_to_pending(client):
    reviewer = create_user(
        username="account_reviewer",
        is_staff=True,
        can_review_usu_id=True,
    )
    member = create_user(
        username="reviewed_account",
        is_usyd_student=True,
        usu_id="11111111",
    )
    member = review_usu_id(
        user=member,
        reviewer=reviewer,
        status=User.UsuReviewStatus.VERIFIED,
    )
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={"is_usyd_student": "on", "usu_id": "22222222"},
    )

    assert response.status_code == 302
    member.refresh_from_db()
    assert member.usu_id == "22222222"
    assert member.usu_review_status == User.UsuReviewStatus.PENDING
    assert member.usu_reviewed_at is None
    assert member.usu_reviewed_by is None


def test_clearing_usyd_declaration_clears_identity_and_review(client):
    reviewer = create_user(
        username="clear_account_reviewer",
        is_staff=True,
        can_review_usu_id=True,
    )
    member = create_user(
        username="clear_account",
        is_usyd_student=True,
        usu_id="12345678",
    )
    member = review_usu_id(
        user=member,
        reviewer=reviewer,
        status=User.UsuReviewStatus.REJECTED,
    )
    client.force_login(member)

    response = client.post(reverse("account"), data={"usu_id": ""})

    assert response.status_code == 302
    member.refresh_from_db()
    assert not member.is_usyd_student
    assert member.usu_id is None
    assert member.usu_review_status == User.UsuReviewStatus.NOT_SUBMITTED
    assert member.usu_reviewed_at is None
    assert member.usu_reviewed_by is None


def test_forged_read_only_and_review_fields_are_ignored(client):
    reviewer = create_user(username="forged_reviewer", is_staff=True)
    member = create_user(username="forged_account")
    original_username = member.username
    original_email = member.email
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={
            "username": "replaced_username",
            "email": "replaced@example.net",
            "is_usyd_student": "on",
            "usu_id": "87654321",
            "usu_review_status": User.UsuReviewStatus.VERIFIED,
            "usu_reviewed_at": "2026-10-24T12:00:00Z",
            "usu_reviewed_by": reviewer.pk,
        },
    )

    assert response.status_code == 302
    member.refresh_from_db()
    assert member.username == original_username
    assert member.email == original_email
    assert member.usu_id == "87654321"
    assert member.usu_review_status == User.UsuReviewStatus.PENDING
    assert member.usu_reviewed_at is None
    assert member.usu_reviewed_by is None


def test_member_update_cannot_modify_another_user(client):
    member = create_user(username="editing_member")
    other = create_user(
        username="protected_member",
        is_usyd_student=True,
        usu_id="11112222",
    )
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={
            "user": other.pk,
            "is_usyd_student": "on",
            "usu_id": "99998888",
        },
    )

    assert response.status_code == 302
    member.refresh_from_db()
    other.refresh_from_db()
    assert member.usu_id == "99998888"
    assert other.usu_id == "11112222"


def test_account_page_links_password_change_and_uses_post_logout(client):
    member = create_user(username="account_actions")
    client.force_login(member)

    response = client.get(reverse("account"))
    content = response.content.decode()

    assert reverse("account_change_password") in content
    assert f'action="{reverse("account_logout")}"' in content
    assert '<form method="post"' in content
