from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Lower, Trim

usu_id_validator = RegexValidator(
    regex=r"^[0-9]+$",
    message="USU ID must contain digits only.",
)


class User(AbstractUser):
    class UsuReviewStatus(models.TextChoices):
        NOT_SUBMITTED = "not_submitted", "Not submitted"
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    email = models.EmailField("email address", unique=True)
    is_usyd_student = models.BooleanField(default=False)
    usu_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        validators=[usu_id_validator],
    )
    usu_review_status = models.CharField(
        max_length=20,
        choices=UsuReviewStatus.choices,
        default=UsuReviewStatus.NOT_SUBMITTED,
    )
    usu_reviewed_at = models.DateTimeField(null=True, blank=True)
    usu_reviewed_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usu_reviews",
    )

    REQUIRED_FIELDS: ClassVar[list[str]] = ["email"]

    class Meta(AbstractUser.Meta):
        permissions: ClassVar[list[tuple[str, str]]] = [
            ("review_usu_id", "Can review USU IDs"),
        ]
        constraints: ClassVar[list[models.CheckConstraint]] = [
            models.CheckConstraint(
                condition=~models.Q(email="") & models.Q(email=Lower(Trim("email"))),
                name="accounts_user_email_normalized",
            ),
            models.CheckConstraint(
                condition=models.Q(usu_id__isnull=True)
                | (
                    models.Q(usu_id=Trim("usu_id"))
                    & models.Q(usu_id__regex=r"^[0-9]+$")
                ),
                name="accounts_user_usu_id_normalized",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        usu_id__isnull=True,
                        usu_review_status="not_submitted",
                        usu_reviewed_at__isnull=True,
                        usu_reviewed_by__isnull=True,
                    )
                    | models.Q(
                        is_usyd_student=True,
                        usu_id__isnull=False,
                        usu_review_status="pending",
                        usu_reviewed_at__isnull=True,
                        usu_reviewed_by__isnull=True,
                    )
                    | models.Q(
                        is_usyd_student=True,
                        usu_id__isnull=False,
                        usu_review_status__in=("verified", "rejected"),
                        usu_reviewed_at__isnull=False,
                    )
                ),
                name="accounts_user_valid_usu_state",
            ),
        ]

    @staticmethod
    def normalize_email_address(email: str | None) -> str:
        return (email or "").strip().lower()

    @staticmethod
    def normalize_usu_id(usu_id: str | None) -> str | None:
        normalized = (usu_id or "").strip()
        return normalized or None

    def clean_fields(self, exclude=None) -> None:
        self._normalize_identity_fields()
        super().clean_fields(exclude=exclude)

    def clean(self) -> None:
        self._normalize_identity_fields()
        super().clean()
        if not self.is_usyd_student and self.usu_id is not None:
            raise ValidationError(
                {"usu_id": "USU ID is only available to USYD students."}
            )

    def save(self, *args, **kwargs) -> None:
        self._normalize_identity_fields()
        if not self.email:
            raise ValidationError({"email": "This field cannot be blank."})
        if self.usu_id is not None:
            usu_id_validator(self.usu_id)

        previous = self._previous_usu_state(using=kwargs.get("using"))
        self._apply_usu_state(previous)
        self._protect_review_transition(previous)

        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
            if {"is_usyd_student", "usu_id"} & update_fields:
                update_fields.update(
                    {
                        "usu_id",
                        "usu_review_status",
                        "usu_reviewed_at",
                        "usu_reviewed_by",
                    }
                )
            kwargs["update_fields"] = update_fields

        super().save(*args, **kwargs)

    def _normalize_identity_fields(self) -> None:
        self.email = self.normalize_email_address(self.email)
        self.usu_id = self.normalize_usu_id(self.usu_id)

    def _previous_usu_state(self, *, using=None) -> dict[str, object] | None:
        if self._state.adding or self.pk is None:
            return None
        return (
            type(self)
            ._base_manager.using(using or self._state.db)
            .filter(pk=self.pk)
            .values(
                "is_usyd_student",
                "usu_id",
                "usu_review_status",
                "usu_reviewed_at",
                "usu_reviewed_by_id",
            )
            .first()
        )

    def _apply_usu_state(self, previous: dict[str, object] | None) -> None:
        if not self.is_usyd_student or self.usu_id is None:
            self.usu_id = None
            self._clear_usu_review(status=self.UsuReviewStatus.NOT_SUBMITTED)
            return

        if previous is None or previous["usu_id"] != self.usu_id:
            self._clear_usu_review(status=self.UsuReviewStatus.PENDING)

    def _protect_review_transition(self, previous: dict[str, object] | None) -> None:
        if previous is None or previous["usu_id"] != self.usu_id:
            return
        if getattr(self, "_allow_usu_review_transition", False):
            return

        review_changed = any(
            (
                previous["usu_review_status"] != self.usu_review_status,
                previous["usu_reviewed_at"] != self.usu_reviewed_at,
                previous["usu_reviewed_by_id"] != self.usu_reviewed_by_id,
            )
        )
        if review_changed:
            raise ValidationError(
                "USU review fields can only be changed through the review service."
            )

    def _clear_usu_review(self, *, status: str) -> None:
        self.usu_review_status = status
        self.usu_reviewed_at = None
        self.usu_reviewed_by = None
