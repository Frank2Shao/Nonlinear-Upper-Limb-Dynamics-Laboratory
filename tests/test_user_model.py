import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.accounts.services import review_usu_id

User = get_user_model()


@pytest.mark.django_db
def test_user_can_be_created_with_standard_permissions() -> None:
    user = User.objects.create_user(
        username="member",
        email="member@example.com",
        password="test-password",
    )

    assert user.username == "member"
    assert user.email == "member@example.com"
    assert user.check_password("test-password")
    assert not user.is_staff
    assert not user.is_superuser
    assert user.groups.count() == 0
    assert user.user_permissions.count() == 0


@pytest.mark.django_db
def test_user_identity_fields_have_safe_defaults() -> None:
    user = User.objects.create_user(
        username="defaults",
        email="defaults@example.com",
        password="test-password",
    )

    assert not user.is_usyd_student
    assert user.usu_id is None
    assert user.usu_review_status == User.UsuReviewStatus.NOT_SUBMITTED
    assert user.usu_reviewed_at is None
    assert user.usu_reviewed_by is None


@pytest.mark.django_db
def test_email_is_required_by_model_validation() -> None:
    user = User(username="missing-email")

    with pytest.raises(ValidationError) as exc_info:
        user.full_clean()

    assert "email" in exc_info.value.message_dict


@pytest.mark.django_db
def test_email_is_unique() -> None:
    User.objects.create_user(
        username="first",
        email="duplicate@example.com",
        password="test-password",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user(
            username="second",
            email="duplicate@example.com",
            password="test-password",
        )


@pytest.mark.django_db
def test_review_fields_are_nullable_and_reviewer_references_user() -> None:
    reviewer = User.objects.create_user(
        username="reviewer",
        email="reviewer@example.com",
        password="test-password",
        is_staff=True,
    )
    reviewer.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="accounts",
            codename="review_usu_id",
        )
    )
    member = User.objects.create_user(
        username="reviewed-member",
        email="reviewed@example.com",
        password="test-password",
        is_usyd_student=True,
        usu_id="12345678",
    )
    member = review_usu_id(
        user=member,
        reviewer=reviewer,
        status=User.UsuReviewStatus.VERIFIED,
    )

    assert member.usu_reviewed_by == reviewer

    reviewer.delete()
    member.refresh_from_db()

    assert member.usu_reviewed_by is None
