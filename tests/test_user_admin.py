import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.accounts.admin import UserAdmin
from apps.accounts.services import review_usu_id, update_usu_identity

User = get_user_model()
PASSWORD = "A-valid-password-2026"
pytestmark = pytest.mark.django_db


def create_user(*, username: str, **extra_fields):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.net",
        password=PASSWORD,
        **extra_fields,
    )


def grant_review_permission(user):
    user.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="accounts",
            codename="review_usu_id",
        )
    )
    return user


def create_reviewer(*, username: str = "usu_reviewer"):
    return grant_review_permission(create_user(username=username, is_staff=True))


def create_submission(*, username: str = "usu_submission", usu_id="00123456"):
    return create_user(
        username=username,
        is_usyd_student=True,
        usu_id=usu_id,
    )


def run_admin_action(client, *, action: str, user):
    return client.post(
        reverse("admin:accounts_user_changelist"),
        data={
            "action": action,
            "_selected_action": [user.pk],
            "index": "0",
        },
    )


def test_custom_user_admin_is_registered_with_review_configuration():
    model_admin = admin.site._registry[User]

    assert isinstance(model_admin, UserAdmin)
    assert model_admin.list_display == (
        "username",
        "email",
        "is_usyd_student",
        "usu_id",
        "usu_review_status",
        "is_active",
    )
    assert model_admin.list_filter == (
        "usu_review_status",
        "is_usyd_student",
        "is_active",
    )
    assert model_admin.search_fields == ("username", "email", "usu_id")
    assert model_admin.actions == ("verify_usu_ids", "reject_usu_ids")


def test_regular_member_cannot_access_user_admin(client):
    member = create_user(username="ordinary_member")
    client.force_login(member)

    response = client.get(reverse("admin:accounts_user_changelist"))

    assert response.status_code == 302
    assert reverse("admin:login") in response.url


def test_staff_without_review_permission_cannot_access_user_admin(client):
    staff = create_user(username="unpermitted_staff", is_staff=True)
    client.force_login(staff)

    response = client.get(reverse("admin:accounts_user_changelist"))

    assert response.status_code == 403


def test_authorized_staff_sees_only_users_with_submitted_usu_ids(client):
    reviewer = create_reviewer()
    submission = create_submission()
    unrelated = create_user(username="unrelated_account")
    client.force_login(reviewer)

    response = client.get(reverse("admin:accounts_user_changelist"))

    assert response.status_code == 200
    content = response.content.decode()
    assert submission.username in content
    assert submission.usu_id in content
    assert unrelated.username not in content
    assert unrelated.email not in content


def test_authorized_staff_has_read_only_review_view(client):
    reviewer = create_reviewer(username="readonly_reviewer")
    submission = create_submission(username="readonly_submission")
    client.force_login(reviewer)

    response = client.get(reverse("admin:accounts_user_change", args=(submission.pk,)))

    assert response.status_code == 200
    assert response.context["has_add_permission"] is False
    assert response.context["has_delete_permission"] is False
    assert response.context["show_save"] is False
    model_admin = admin.site._registry[User]
    assert set(model_admin.get_readonly_fields(response.wsgi_request, submission)) == {
        "username",
        "email",
        "is_active",
        "is_usyd_student",
        "usu_id",
        "usu_review_status",
        "usu_reviewed_at",
        "usu_reviewed_by",
    }


def test_authorized_staff_cannot_add_or_delete_users(client):
    reviewer = create_reviewer(username="limited_reviewer")
    submission = create_submission(username="protected_submission")
    client.force_login(reviewer)

    add_response = client.get(reverse("admin:accounts_user_add"))
    delete_response = client.get(
        reverse("admin:accounts_user_delete", args=(submission.pk,))
    )

    assert add_response.status_code == 403
    assert delete_response.status_code == 403


def test_authorized_staff_cannot_forge_review_fields_through_change_form(client):
    reviewer = create_reviewer(username="forged_admin_reviewer")
    submission = create_submission(username="forged_admin_submission")
    client.force_login(reviewer)

    response = client.post(
        reverse("admin:accounts_user_change", args=(submission.pk,)),
        data={
            "username": submission.username,
            "email": submission.email,
            "usu_review_status": User.UsuReviewStatus.VERIFIED,
            "usu_reviewed_by": reviewer.pk,
            "_save": "Save",
        },
    )

    assert response.status_code in {200, 403}
    submission.refresh_from_db()
    assert submission.usu_review_status == User.UsuReviewStatus.PENDING
    assert submission.usu_reviewed_at is None
    assert submission.usu_reviewed_by is None


def test_superuser_retains_standard_user_admin_access(client):
    superuser = User.objects.create_superuser(
        username="admin_superuser",
        email="admin-superuser@example.net",
        password=PASSWORD,
    )
    client.force_login(superuser)

    changelist_response = client.get(reverse("admin:accounts_user_changelist"))
    add_response = client.get(reverse("admin:accounts_user_add"))

    assert changelist_response.status_code == 200
    assert add_response.status_code == 200


@pytest.mark.parametrize(
    ("action", "expected_status"),
    [
        ("verify_usu_ids", User.UsuReviewStatus.VERIFIED),
        ("reject_usu_ids", User.UsuReviewStatus.REJECTED),
    ],
)
def test_review_actions_record_status_reviewer_and_time(
    client,
    action: str,
    expected_status: str,
):
    reviewer = create_reviewer(username=f"{expected_status}_admin")
    submission = create_submission(username=f"{expected_status}_submission")
    client.force_login(reviewer)

    response = run_admin_action(client, action=action, user=submission)

    assert response.status_code == 302
    submission.refresh_from_db()
    assert submission.usu_review_status == expected_status
    assert submission.usu_reviewed_by == reviewer
    assert submission.usu_reviewed_at is not None


def test_resubmitted_usu_id_can_be_reviewed_again(client):
    first_reviewer = create_reviewer(username="first_reviewer")
    second_reviewer = create_reviewer(username="second_reviewer")
    submission = create_submission(username="resubmitted_member", usu_id="11111111")
    reviewed = review_usu_id(
        user=submission,
        reviewer=first_reviewer,
        status=User.UsuReviewStatus.VERIFIED,
    )
    first_reviewed_at = reviewed.usu_reviewed_at
    resubmitted = update_usu_identity(
        user=reviewed,
        is_usyd_student=True,
        usu_id="22222222",
    )
    client.force_login(second_reviewer)

    response = run_admin_action(
        client,
        action="verify_usu_ids",
        user=resubmitted,
    )

    assert response.status_code == 302
    resubmitted.refresh_from_db()
    assert resubmitted.usu_review_status == User.UsuReviewStatus.VERIFIED
    assert resubmitted.usu_reviewed_by == second_reviewer
    assert resubmitted.usu_reviewed_at is not None
    assert resubmitted.usu_reviewed_at > first_reviewed_at


def test_deactivating_reviewer_preserves_existing_audit_record():
    reviewer = create_reviewer(username="former_reviewer")
    submission = create_submission(username="historical_submission")
    reviewed = review_usu_id(
        user=submission,
        reviewer=reviewer,
        status=User.UsuReviewStatus.REJECTED,
    )
    reviewed_at = reviewed.usu_reviewed_at

    User.objects.filter(pk=reviewer.pk).update(is_active=False)
    reviewed.refresh_from_db()

    assert reviewed.usu_review_status == User.UsuReviewStatus.REJECTED
    assert reviewed.usu_reviewed_by == reviewer
    assert reviewed.usu_reviewed_at == reviewed_at


def test_account_response_does_not_expose_review_audit_metadata(client):
    reviewer = create_reviewer(username="private_review_actor")
    submission = create_submission(username="private_audit_member")
    reviewed = review_usu_id(
        user=submission,
        reviewer=reviewer,
        status=User.UsuReviewStatus.VERIFIED,
    )
    client.force_login(reviewed)

    response = client.get(reverse("account"))
    content = response.content.decode()

    assert response.status_code == 200
    assert reviewer.username not in content
    assert reviewed.usu_reviewed_at.isoformat() not in content


def test_anonymous_response_does_not_expose_full_usu_id(client):
    submission = create_submission(username="private_usu_id")

    response = client.get(reverse("account"))

    assert response.status_code == 302
    assert submission.usu_id not in response.content.decode()
