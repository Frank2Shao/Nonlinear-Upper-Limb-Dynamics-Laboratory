import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction

from apps.accounts.services import review_usu_id, update_usu_identity

User = get_user_model()


def create_user(username: str, **extra_fields):
    can_review_usu_id = extra_fields.pop("can_review_usu_id", False)
    user = User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="test-password",
        **extra_fields,
    )
    if can_review_usu_id:
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="accounts",
                codename="review_usu_id",
            )
        )
    return user


@pytest.mark.django_db
def test_email_is_trimmed_and_lowercased() -> None:
    user = User.objects.create_user(
        username="normalized-email",
        email="  Member@Example.COM  ",
        password="test-password",
    )

    assert user.email == "member@example.com"


@pytest.mark.django_db
def test_normalized_email_uniqueness_is_case_insensitive() -> None:
    User.objects.create_user(
        username="first-case",
        email="member@example.com",
        password="test-password",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user(
            username="second-case",
            email="MEMBER@EXAMPLE.COM",
            password="test-password",
        )


@pytest.mark.django_db
def test_database_rejects_non_normalized_email_direct_write() -> None:
    user = create_user("direct-email")

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.filter(pk=user.pk).update(email="Direct@Example.COM")


@pytest.mark.django_db
def test_non_usyd_user_cannot_submit_usu_id() -> None:
    user = create_user("non-usyd")

    with pytest.raises(ValidationError) as exc_info:
        update_usu_identity(
            user=user,
            is_usyd_student=False,
            usu_id="12345678",
        )

    assert "usu_id" in exc_info.value.message_dict


@pytest.mark.django_db
def test_usyd_user_can_leave_usu_id_blank() -> None:
    user = create_user("blank-id")

    updated = update_usu_identity(
        user=user,
        is_usyd_student=True,
        usu_id="   ",
    )

    assert updated.is_usyd_student
    assert updated.usu_id is None
    assert updated.usu_review_status == User.UsuReviewStatus.NOT_SUBMITTED
    assert updated.usu_reviewed_at is None
    assert updated.usu_reviewed_by is None


@pytest.mark.django_db
def test_usu_id_accepts_digits_only_and_preserves_leading_zeroes() -> None:
    user = create_user("numeric-id")

    updated = update_usu_identity(
        user=user,
        is_usyd_student=True,
        usu_id="  00123456  ",
    )

    assert updated.usu_id == "00123456"
    assert updated.usu_review_status == User.UsuReviewStatus.PENDING

    with pytest.raises(ValidationError) as exc_info:
        update_usu_identity(
            user=updated,
            is_usyd_student=True,
            usu_id="12A456",
        )

    assert "usu_id" in exc_info.value.message_dict


@pytest.mark.django_db
def test_first_usu_id_submission_enters_pending() -> None:
    user = create_user("first-id")

    updated = update_usu_identity(
        user=user,
        is_usyd_student=True,
        usu_id="12345678",
    )

    assert updated.usu_review_status == User.UsuReviewStatus.PENDING
    assert updated.usu_reviewed_at is None
    assert updated.usu_reviewed_by is None


@pytest.mark.django_db
def test_changing_verified_usu_id_resets_review() -> None:
    reviewer = create_user(
        "change-reviewer",
        is_staff=True,
        can_review_usu_id=True,
    )
    member = create_user(
        "change-member",
        is_usyd_student=True,
        usu_id="11111111",
    )
    reviewed = review_usu_id(
        user=member,
        reviewer=reviewer,
        status=User.UsuReviewStatus.VERIFIED,
    )

    updated = update_usu_identity(
        user=reviewed,
        is_usyd_student=True,
        usu_id="22222222",
    )

    assert updated.usu_review_status == User.UsuReviewStatus.PENDING
    assert updated.usu_reviewed_at is None
    assert updated.usu_reviewed_by is None


@pytest.mark.django_db
def test_resubmitting_same_usu_id_preserves_review() -> None:
    reviewer = create_user(
        "same-reviewer",
        is_staff=True,
        can_review_usu_id=True,
    )
    member = create_user(
        "same-member",
        is_usyd_student=True,
        usu_id="12345678",
    )
    reviewed = review_usu_id(
        user=member,
        reviewer=reviewer,
        status=User.UsuReviewStatus.VERIFIED,
    )

    updated = update_usu_identity(
        user=reviewed,
        is_usyd_student=True,
        usu_id=" 12345678 ",
    )

    assert updated.usu_review_status == User.UsuReviewStatus.VERIFIED
    assert updated.usu_reviewed_at == reviewed.usu_reviewed_at
    assert updated.usu_reviewed_by == reviewer


@pytest.mark.django_db
def test_clearing_usu_id_resets_to_not_submitted() -> None:
    reviewer = create_user(
        "clear-reviewer",
        is_staff=True,
        can_review_usu_id=True,
    )
    member = create_user(
        "clear-member",
        is_usyd_student=True,
        usu_id="12345678",
    )
    reviewed = review_usu_id(
        user=member,
        reviewer=reviewer,
        status=User.UsuReviewStatus.VERIFIED,
    )

    updated = update_usu_identity(
        user=reviewed,
        is_usyd_student=True,
        usu_id=None,
    )

    assert updated.usu_id is None
    assert updated.usu_review_status == User.UsuReviewStatus.NOT_SUBMITTED
    assert updated.usu_reviewed_at is None
    assert updated.usu_reviewed_by is None


@pytest.mark.django_db
def test_cancelling_usyd_declaration_clears_identity_and_review() -> None:
    reviewer = create_user(
        "cancel-reviewer",
        is_staff=True,
        can_review_usu_id=True,
    )
    member = create_user(
        "cancel-member",
        is_usyd_student=True,
        usu_id="12345678",
    )
    reviewed = review_usu_id(
        user=member,
        reviewer=reviewer,
        status=User.UsuReviewStatus.VERIFIED,
    )

    updated = update_usu_identity(
        user=reviewed,
        is_usyd_student=False,
        usu_id=None,
    )

    assert not updated.is_usyd_student
    assert updated.usu_id is None
    assert updated.usu_review_status == User.UsuReviewStatus.NOT_SUBMITTED
    assert updated.usu_reviewed_at is None
    assert updated.usu_reviewed_by is None


@pytest.mark.django_db
def test_non_staff_user_cannot_review_usu_id() -> None:
    member = create_user(
        "unauthorized-member",
        is_usyd_student=True,
        usu_id="12345678",
    )
    non_staff = create_user("non-staff-reviewer")

    with pytest.raises(PermissionDenied):
        review_usu_id(
            user=member,
            reviewer=non_staff,
            status=User.UsuReviewStatus.VERIFIED,
        )


@pytest.mark.django_db
def test_staff_without_review_permission_cannot_review_usu_id() -> None:
    member = create_user(
        "unpermitted-review-member",
        is_usyd_student=True,
        usu_id="12345678",
    )
    staff = create_user("unpermitted-reviewer", is_staff=True)

    with pytest.raises(PermissionDenied):
        review_usu_id(
            user=member,
            reviewer=staff,
            status=User.UsuReviewStatus.VERIFIED,
        )


@pytest.mark.django_db
def test_inactive_staff_user_cannot_review_usu_id() -> None:
    member = create_user(
        "inactive-review-member",
        is_usyd_student=True,
        usu_id="12345678",
    )
    inactive_staff = create_user(
        "inactive-reviewer",
        is_staff=True,
        is_active=False,
        can_review_usu_id=True,
    )

    with pytest.raises(PermissionDenied):
        review_usu_id(
            user=member,
            reviewer=inactive_staff,
            status=User.UsuReviewStatus.VERIFIED,
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [User.UsuReviewStatus.VERIFIED, User.UsuReviewStatus.REJECTED],
)
def test_staff_review_records_status_reviewer_and_time(status: str) -> None:
    reviewer = create_user(
        f"{status}-reviewer",
        is_staff=True,
        can_review_usu_id=True,
    )
    member = create_user(
        f"{status}-member",
        is_usyd_student=True,
        usu_id="12345678",
    )

    reviewed = review_usu_id(user=member, reviewer=reviewer, status=status)

    assert reviewed.usu_review_status == status
    assert reviewed.usu_reviewed_at is not None
    assert reviewed.usu_reviewed_by == reviewer


@pytest.mark.django_db
def test_direct_model_save_cannot_change_review_fields() -> None:
    member = create_user(
        "direct-review",
        is_usyd_student=True,
        usu_id="12345678",
    )
    member.usu_review_status = User.UsuReviewStatus.VERIFIED

    with pytest.raises(ValidationError):
        member.save()


@pytest.mark.django_db
def test_database_rejects_non_usyd_user_with_usu_id() -> None:
    user = create_user("database-non-usyd")

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.filter(pk=user.pk).update(usu_id="12345678")


@pytest.mark.django_db
def test_database_rejects_non_numeric_usu_id() -> None:
    user = create_user("database-id", is_usyd_student=True)

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.filter(pk=user.pk).update(
            usu_id="12A456",
            usu_review_status=User.UsuReviewStatus.PENDING,
        )


@pytest.mark.django_db
def test_database_rejects_reviewed_status_without_review_time() -> None:
    user = create_user(
        "database-review",
        is_usyd_student=True,
        usu_id="12345678",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.filter(pk=user.pk).update(
            usu_review_status=User.UsuReviewStatus.VERIFIED,
        )
