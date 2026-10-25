from typing import ClassVar

from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    RegexValidator,
    URLValidator,
)
from django.db import models
from django.db.models import Exists, OuterRef
from django.db.models.functions import Lower, Trim
from django.utils.html import strip_tags
from PIL import Image, UnidentifiedImageError

MAX_AVATAR_SIZE = 5 * 1024 * 1024
ALLOWED_AVATAR_FORMATS = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}
instagram_handle_validator = RegexValidator(
    regex=r"^[A-Za-z0-9._]+$",
    message="Enter an Instagram username, not a URL.",
)


def validate_avatar(uploaded_file) -> None:
    if uploaded_file.size > MAX_AVATAR_SIZE:
        raise ValidationError("Avatar files must be 5 MB or smaller.")

    original_position = uploaded_file.tell()
    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        detected_format = image.format
        image.verify()
    except (OSError, UnidentifiedImageError, ValueError) as exc:
        raise ValidationError("Upload a valid JPG, PNG, or WebP image.") from exc
    finally:
        uploaded_file.seek(original_position)

    expected_mime = ALLOWED_AVATAR_FORMATS.get(detected_format)
    if expected_mime is None:
        raise ValidationError("Upload a valid JPG, PNG, or WebP image.")

    declared_mime = getattr(uploaded_file, "content_type", None)
    if declared_mime is None:
        declared_mime = getattr(
            getattr(uploaded_file, "file", None),
            "content_type",
            None,
        )
    if declared_mime is not None and declared_mime != expected_mime:
        raise ValidationError("The avatar file type does not match its image content.")


def validate_plain_text(value: str) -> None:
    if strip_tags(value) != value:
        raise ValidationError("Bio must contain plain text only.")


def validate_https_url(value: str) -> None:
    URLValidator(schemes=["https"])(value)
    if not value.lower().startswith("https://"):
        raise ValidationError("Use an HTTPS URL.")


class MemberProfileQuerySet(models.QuerySet):
    def public(self):
        verified_email = EmailAddress.objects.filter(
            user_id=OuterRef("user_id"),
            verified=True,
        )
        return self.annotate(
            has_verified_email=Exists(verified_email),
        ).filter(
            is_published=True,
            is_hidden_by_admin=False,
            user__is_active=True,
            has_verified_email=True,
        )


class MemberProfile(models.Model):
    class ExperienceLevel(models.TextChoices):
        NOT_SPECIFIED = "not_spec", "Not specified"
        UNDER_ONE_YEAR = "under_one", "< 1 year"
        ONE_TO_THREE_YEARS = "one_to_three", "1–3 years"
        OVER_THREE_YEARS = "over_three", "> 3 years"

    class PreferredArm(models.TextChoices):
        NOT_SPECIFIED = "not_spec", "Not specified"
        LEFT = "left", "Left"
        RIGHT = "right", "Right"
        BOTH = "both", "Both"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )
    display_name = models.CharField(max_length=80, null=True, blank=True)
    avatar = models.ImageField(
        upload_to="member_avatars/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            validate_avatar,
        ],
    )
    bio = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        validators=[validate_plain_text],
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.NOT_SPECIFIED,
    )
    preferred_arm = models.CharField(
        max_length=20,
        choices=PreferredArm.choices,
        default=PreferredArm.NOT_SPECIFIED,
    )
    instagram_handle = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        validators=[instagram_handle_validator],
    )
    other_social_url = models.URLField(
        null=True,
        blank=True,
        validators=[validate_https_url],
    )
    is_published = models.BooleanField(default=False)
    is_hidden_by_admin = models.BooleanField(default=False)
    executive_role = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: ClassVar[models.Manager] = MemberProfileQuerySet.as_manager()

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                condition=models.Q(display_name__isnull=True)
                | (
                    ~models.Q(display_name="")
                    & models.Q(display_name=Trim("display_name"))
                ),
                name="members_profile_display_name_normalized",
            ),
            models.UniqueConstraint(
                Lower("display_name"),
                condition=models.Q(display_name__isnull=False),
                name="members_profile_display_name_ci_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(other_social_url__isnull=True)
                | models.Q(other_social_url__startswith="https://"),
                name="members_profile_social_url_https",
            ),
        ]

    def __str__(self) -> str:
        return self.display_name or self.user.get_username()

    @property
    def resolved_display_name(self) -> str:
        return self.display_name or self.user.get_username()

    def clean(self) -> None:
        self._normalize_optional_fields()
        super().clean()

    def save(self, *args, **kwargs) -> None:
        self._normalize_optional_fields()
        self.full_clean()
        super().save(*args, **kwargs)

    def _normalize_optional_fields(self) -> None:
        self.display_name = self._optional_text(self.display_name)
        self.bio = self._optional_text(self.bio)
        self.executive_role = self._optional_text(self.executive_role)
        other_social_url = self._optional_text(self.other_social_url)
        if other_social_url is not None and other_social_url.lower().startswith(
            "https://"
        ):
            other_social_url = f"https://{other_social_url[8:]}"
        self.other_social_url = other_social_url

        instagram_handle = self._optional_text(self.instagram_handle)
        if instagram_handle is not None:
            instagram_handle = instagram_handle.removeprefix("@").strip()
        self.instagram_handle = instagram_handle or None

    @staticmethod
    def _optional_text(value: str | None) -> str | None:
        normalized = (value or "").strip()
        return normalized or None
