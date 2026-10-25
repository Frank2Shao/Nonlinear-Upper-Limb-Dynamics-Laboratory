from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from .models import User, usu_id_validator


@transaction.atomic
def update_usu_identity(
    *,
    user: User,
    is_usyd_student: bool,
    usu_id: str | None,
) -> User:
    normalized_usu_id = User.normalize_usu_id(usu_id)
    if normalized_usu_id is not None:
        try:
            usu_id_validator(normalized_usu_id)
        except ValidationError as exc:
            raise ValidationError({"usu_id": exc.messages}) from exc
    if not is_usyd_student and normalized_usu_id is not None:
        raise ValidationError({"usu_id": "USU ID is only available to USYD students."})

    locked_user = User.objects.select_for_update().get(pk=user.pk)
    locked_user.is_usyd_student = is_usyd_student
    locked_user.usu_id = normalized_usu_id
    locked_user.save()
    return locked_user


@transaction.atomic
def review_usu_id(*, user: User, reviewer: User, status: str) -> User:
    try:
        review_status = User.UsuReviewStatus(status)
    except ValueError as exc:
        raise ValidationError({"status": "Unsupported USU review status."}) from exc
    if review_status not in {
        User.UsuReviewStatus.VERIFIED,
        User.UsuReviewStatus.REJECTED,
    }:
        raise ValidationError({"status": "USU review must verify or reject an ID."})

    locked_reviewer = User.objects.select_for_update().get(pk=reviewer.pk)
    if (
        not locked_reviewer.is_active
        or not locked_reviewer.is_staff
        or not locked_reviewer.has_perm("accounts.review_usu_id")
    ):
        raise PermissionDenied(
            "An active staff account with USU review permission is required."
        )

    locked_user = User.objects.select_for_update().get(pk=user.pk)
    if not locked_user.is_usyd_student or locked_user.usu_id is None:
        raise ValidationError(
            {"usu_id": "A submitted USU ID is required before review."}
        )

    locked_user.usu_review_status = review_status
    locked_user.usu_reviewed_at = timezone.now()
    locked_user.usu_reviewed_by = locked_reviewer
    locked_user._allow_usu_review_transition = True
    try:
        locked_user.full_clean()
        locked_user.save()
    finally:
        del locked_user._allow_usu_review_transition
    return locked_user
