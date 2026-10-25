from io import BytesIO

import pytest
from allauth.account.models import EmailAddress
from django.contrib.admin import AdminSite
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from PIL import Image

from apps.accounts.models import User
from apps.members.admin import MemberProfileAdmin
from apps.members.forms import MemberProfileForm
from apps.members.models import MAX_AVATAR_SIZE, MemberProfile
from apps.members.services import ensure_member_profile

pytestmark = pytest.mark.django_db


def create_user(*, username: str, is_active: bool = True) -> User:
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="test-password",
        is_active=is_active,
    )


def create_image_upload(
    *,
    image_format: str = "PNG",
    filename: str = "avatar.png",
    content_type: str = "image/png",
) -> SimpleUploadedFile:
    image_bytes = BytesIO()
    Image.new("RGB", (2, 2), color="gold").save(image_bytes, format=image_format)
    return SimpleUploadedFile(
        filename,
        image_bytes.getvalue(),
        content_type=content_type,
    )


def test_profile_defaults_relationship_and_display_name_fallback():
    user = create_user(username="member")

    profile = MemberProfile.objects.create(user=user)

    assert profile.user == user
    assert profile.resolved_display_name == "member"
    assert profile.display_name is None
    assert profile.avatar.name is None
    assert profile.bio is None
    assert profile.experience_level == MemberProfile.ExperienceLevel.NOT_SPECIFIED
    assert profile.preferred_arm == MemberProfile.PreferredArm.NOT_SPECIFIED
    assert profile.instagram_handle is None
    assert profile.other_social_url is None
    assert profile.is_published is False
    assert profile.is_hidden_by_admin is False
    assert profile.executive_role is None
    assert profile.created_at is not None
    assert profile.updated_at is not None


def test_profile_is_one_to_one_and_deleted_with_user():
    user = create_user(username="owner")
    MemberProfile.objects.create(user=user)

    with pytest.raises(ValidationError):
        MemberProfile.objects.create(user=user)

    user.delete()
    assert MemberProfile.objects.count() == 0


def test_ensure_member_profile_is_idempotent():
    user = create_user(username="idempotent")

    first, first_created = ensure_member_profile(user=user)
    second, second_created = ensure_member_profile(user=user)

    assert first_created is True
    assert second_created is False
    assert first.pk == second.pk
    assert MemberProfile.objects.filter(user=user).count() == 1


def test_updated_at_changes_on_save():
    profile = MemberProfile.objects.create(user=create_user(username="timestamp"))
    original_updated_at = profile.updated_at

    profile.bio = "Updated biography"
    profile.save()
    profile.refresh_from_db()

    assert profile.updated_at > original_updated_at


def test_display_name_is_trimmed_and_blank_becomes_null():
    profile = MemberProfile.objects.create(
        user=create_user(username="clean-name"),
        display_name="  Club Member  ",
    )
    assert profile.display_name == "Club Member"

    profile.display_name = "   "
    profile.save()
    profile.refresh_from_db()
    assert profile.display_name is None


def test_multiple_profiles_can_have_null_display_name():
    MemberProfile.objects.create(user=create_user(username="anonymous-one"))
    MemberProfile.objects.create(user=create_user(username="anonymous-two"))

    assert MemberProfile.objects.filter(display_name__isnull=True).count() == 2


def test_display_name_is_unique_ignoring_case():
    MemberProfile.objects.create(
        user=create_user(username="first-name"),
        display_name="Arm Wrestler",
    )

    with pytest.raises(ValidationError):
        MemberProfile.objects.create(
            user=create_user(username="second-name"),
            display_name="arm wrestler",
        )


def test_database_rejects_non_normalized_display_name():
    profile = MemberProfile.objects.create(user=create_user(username="db-name"))

    with pytest.raises(IntegrityError), transaction.atomic():
        MemberProfile.objects.filter(pk=profile.pk).update(display_name=" padded ")


@pytest.mark.parametrize(
    ("image_format", "filename", "content_type"),
    [
        ("JPEG", "avatar.jpg", "image/jpeg"),
        ("PNG", "avatar.png", "image/png"),
        ("WEBP", "avatar.webp", "image/webp"),
    ],
)
def test_avatar_accepts_supported_real_images(
    settings, tmp_path, image_format, filename, content_type
):
    settings.MEDIA_ROOT = tmp_path
    profile = MemberProfile.objects.create(
        user=create_user(username=f"image-{image_format.lower()}"),
        avatar=create_image_upload(
            image_format=image_format,
            filename=filename,
            content_type=content_type,
        ),
    )

    assert profile.avatar.name.startswith("member_avatars/")


def test_avatar_rejects_disguised_non_image(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    upload = SimpleUploadedFile("avatar.png", b"not an image", content_type="image/png")

    with pytest.raises(ValidationError):
        MemberProfile.objects.create(
            user=create_user(username="fake-image"),
            avatar=upload,
        )


def test_avatar_rejects_mismatched_mime(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    with pytest.raises(ValidationError):
        MemberProfile.objects.create(
            user=create_user(username="wrong-mime"),
            avatar=create_image_upload(content_type="image/jpeg"),
        )


def test_avatar_rejects_files_larger_than_five_mb(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    valid_png = create_image_upload().read()
    oversized = valid_png + b"0" * (MAX_AVATAR_SIZE - len(valid_png) + 1)
    upload = SimpleUploadedFile("large.png", oversized, content_type="image/png")

    with pytest.raises(ValidationError):
        MemberProfile.objects.create(
            user=create_user(username="large-image"),
            avatar=upload,
        )


def test_bio_accepts_plain_text_and_rejects_html():
    plain_profile = MemberProfile.objects.create(
        user=create_user(username="plain-bio"),
        bio="Training for two years.\nRight-arm specialist.",
    )
    assert plain_profile.bio.startswith("Training")

    with pytest.raises(ValidationError):
        MemberProfile.objects.create(
            user=create_user(username="html-bio"),
            bio="<strong>Experienced</strong>",
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("experience_level", "invalid"),
        ("preferred_arm", "invalid"),
    ],
)
def test_choice_fields_reject_unknown_values(field, value):
    profile = MemberProfile(user=create_user(username=f"choice-{field}"))
    setattr(profile, field, value)

    with pytest.raises(ValidationError):
        profile.save()


def test_instagram_handle_is_cleaned_and_must_be_a_username():
    profile = MemberProfile.objects.create(
        user=create_user(username="instagram"),
        instagram_handle="  @club.member_1  ",
    )
    assert profile.instagram_handle == "club.member_1"

    with pytest.raises(ValidationError):
        MemberProfile.objects.create(
            user=create_user(username="instagram-url"),
            instagram_handle="https://instagram.com/club",
        )


def test_other_social_url_allows_https_only():
    profile = MemberProfile.objects.create(
        user=create_user(username="https-social"),
        other_social_url="  HTTPS://example.com/member  ",
    )
    assert profile.other_social_url == "https://example.com/member"

    with pytest.raises(ValidationError):
        MemberProfile.objects.create(
            user=create_user(username="http-social"),
            other_social_url="http://example.com/member",
        )


def test_public_queryset_enforces_every_visibility_condition():
    visible_user = create_user(username="visible")
    visible = MemberProfile.objects.create(user=visible_user, is_published=True)
    EmailAddress.objects.create(
        user=visible_user,
        email=visible_user.email,
        verified=True,
        primary=True,
    )

    unpublished_user = create_user(username="unpublished")
    MemberProfile.objects.create(user=unpublished_user)
    EmailAddress.objects.create(
        user=unpublished_user,
        email=unpublished_user.email,
        verified=True,
    )

    hidden_user = create_user(username="hidden")
    MemberProfile.objects.create(
        user=hidden_user,
        is_published=True,
        is_hidden_by_admin=True,
    )
    EmailAddress.objects.create(
        user=hidden_user,
        email=hidden_user.email,
        verified=True,
    )

    inactive_user = create_user(username="inactive", is_active=False)
    MemberProfile.objects.create(user=inactive_user, is_published=True)
    EmailAddress.objects.create(
        user=inactive_user,
        email=inactive_user.email,
        verified=True,
    )

    unverified_user = create_user(username="unverified")
    MemberProfile.objects.create(user=unverified_user, is_published=True)
    EmailAddress.objects.create(
        user=unverified_user,
        email=unverified_user.email,
        verified=False,
    )

    assert list(MemberProfile.objects.public()) == [visible]


def test_member_form_excludes_admin_managed_and_timestamp_fields():
    expected_fields = {
        "display_name",
        "avatar",
        "bio",
        "experience_level",
        "preferred_arm",
        "instagram_handle",
        "other_social_url",
        "is_published",
    }

    assert set(MemberProfileForm.base_fields) == expected_fields
    assert "is_hidden_by_admin" not in MemberProfileForm.base_fields
    assert "executive_role" not in MemberProfileForm.base_fields
    assert "created_at" not in MemberProfileForm.base_fields
    assert "updated_at" not in MemberProfileForm.base_fields


def test_member_form_cannot_modify_admin_managed_fields():
    profile = MemberProfile.objects.create(
        user=create_user(username="form-member"),
        is_hidden_by_admin=True,
        executive_role="President",
    )
    form = MemberProfileForm(
        data={
            "display_name": "Updated Member",
            "experience_level": MemberProfile.ExperienceLevel.UNDER_ONE_YEAR,
            "preferred_arm": MemberProfile.PreferredArm.LEFT,
            "is_published": True,
            "is_hidden_by_admin": False,
            "executive_role": "Changed by member",
        },
        instance=profile,
    )

    assert form.is_valid(), form.errors
    saved = form.save()
    assert saved.display_name == "Updated Member"
    assert saved.is_hidden_by_admin is True
    assert saved.executive_role == "President"


def test_profile_admin_exposes_management_fields_with_read_only_timestamps():
    profile_admin = MemberProfileAdmin(MemberProfile, AdminSite())

    assert "is_hidden_by_admin" in profile_admin.list_display
    assert "is_published" in profile_admin.list_filter
    assert profile_admin.readonly_fields == ("created_at", "updated_at")
