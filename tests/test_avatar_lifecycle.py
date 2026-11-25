import re
from io import BytesIO
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import RequestFactory, override_settings
from django.urls import resolve, reverse
from PIL import Image

from apps.members.models import MAX_AVATAR_SIZE, MemberProfile
from config.urls import development_media_urlpatterns
from tests.factories import create_member

pytestmark = pytest.mark.django_db


def image_bytes(*, image_format: str = "PNG", size: tuple[int, int] = (4, 3)):
    output = BytesIO()
    Image.new("RGB", size, color="gold").save(output, format=image_format)
    return output.getvalue()


def image_upload(
    *,
    filename: str = "avatar.png",
    image_format: str = "PNG",
    content_type: str = "image/png",
    content: bytes | None = None,
):
    return SimpleUploadedFile(
        filename,
        content if content is not None else image_bytes(image_format=image_format),
        content_type=content_type,
    )


def create_member_with_avatar(*, username: str, avatar=None):
    return create_member(username, avatar=avatar)


def profile_data(**overrides):
    data = {
        "display_name": "",
        "bio": "",
        "experience_level": MemberProfile.ExperienceLevel.NOT_SPECIFIED,
        "preferred_arm": MemberProfile.PreferredArm.NOT_SPECIFIED,
        "instagram_handle": "",
        "other_social_url": "",
    }
    data.update(overrides)
    return data


def stored_avatar_path(settings, profile: MemberProfile) -> Path:
    return Path(settings.MEDIA_ROOT, profile.avatar.name)


def test_avatar_upload_preserves_original_bytes(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    member, profile = create_member_with_avatar(username="avatar-original")
    client.force_login(member)
    original = image_bytes(size=(7, 5))

    response = client.post(
        reverse("members:profile_edit"),
        data=profile_data(avatar=image_upload(content=original)),
    )

    assert response.status_code == 302
    profile.refresh_from_db()
    assert stored_avatar_path(settings, profile).read_bytes() == original


def test_avatar_rejects_extension_that_does_not_match_content(
    client, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    member, profile = create_member_with_avatar(username="avatar-extension")
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=profile_data(
            avatar=image_upload(
                filename="avatar.jpg",
                content_type="image/png",
            )
        ),
    )

    assert response.status_code == 200
    assert response.context["form"].errors["avatar"] == [
        "The avatar filename does not match its image content."
    ]
    profile.refresh_from_db()
    assert not profile.avatar


def test_avatar_accepts_exactly_five_mb_and_rejects_one_byte_more(
    client, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    member, profile = create_member_with_avatar(username="avatar-size")
    client.force_login(member)
    png = image_bytes()

    accepted = client.post(
        reverse("members:profile_edit"),
        data=profile_data(
            avatar=image_upload(content=png + b"0" * (MAX_AVATAR_SIZE - len(png)))
        ),
    )

    assert accepted.status_code == 302
    profile.refresh_from_db()
    accepted_name = profile.avatar.name

    rejected = client.post(
        reverse("members:profile_edit"),
        data=profile_data(
            avatar=image_upload(content=png + b"0" * (MAX_AVATAR_SIZE - len(png) + 1))
        ),
    )

    assert rejected.status_code == 200
    assert rejected.context["form"].errors["avatar"] == [
        "Avatar files must be 5 MB or smaller."
    ]
    profile.refresh_from_db()
    assert profile.avatar.name == accepted_name
    assert stored_avatar_path(settings, profile).exists()


def test_replacing_avatar_deletes_old_file_and_keeps_only_new_file(
    client, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    member, profile = create_member_with_avatar(
        username="avatar-replace",
        avatar=image_upload(filename="old.png"),
    )
    old_path = stored_avatar_path(settings, profile)
    client.force_login(member)
    replacement = image_bytes(size=(8, 6))

    response = client.post(
        reverse("members:profile_edit"),
        data=profile_data(avatar=image_upload(filename="new.png", content=replacement)),
    )

    assert response.status_code == 302
    profile.refresh_from_db()
    new_path = stored_avatar_path(settings, profile)
    assert new_path.read_bytes() == replacement
    assert not old_path.exists()
    assert list(tmp_path.rglob("*.*")) == [new_path]


def test_removing_avatar_deletes_file(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    member, profile = create_member_with_avatar(
        username="avatar-remove",
        avatar=image_upload(filename="remove.png"),
    )
    old_path = stored_avatar_path(settings, profile)
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=profile_data(remove_avatar="on"),
    )

    assert response.status_code == 302
    profile.refresh_from_db()
    assert not profile.avatar
    assert not old_path.exists()
    assert list(tmp_path.rglob("*.*")) == []


def test_profile_update_keeps_existing_avatar_after_form_validation(
    client, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    member, profile = create_member_with_avatar(
        username="avatar-keep",
        avatar=image_upload(filename="keep.png"),
    )
    original_name = profile.avatar.name
    original_bytes = stored_avatar_path(settings, profile).read_bytes()
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=profile_data(display_name="Avatar Keeper"),
    )

    assert response.status_code == 302
    profile.refresh_from_db()
    assert profile.display_name == "Avatar Keeper"
    assert profile.avatar.name == original_name
    assert stored_avatar_path(settings, profile).read_bytes() == original_bytes


def test_invalid_update_keeps_current_avatar_and_creates_no_orphan(
    client, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    member, profile = create_member_with_avatar(
        username="avatar-invalid",
        avatar=image_upload(filename="current.png"),
    )
    old_name = profile.avatar.name
    old_path = stored_avatar_path(settings, profile)
    old_bytes = old_path.read_bytes()
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=profile_data(
            avatar=image_upload(content=b"not an image"),
            remove_avatar="on",
        ),
    )

    assert response.status_code == 200
    assert response.context["form"].errors["avatar"]
    profile.refresh_from_db()
    assert profile.avatar.name == old_name
    assert old_path.read_bytes() == old_bytes
    assert list(tmp_path.rglob("*.*")) == [old_path]


def test_save_failure_removes_new_file_and_preserves_current_avatar(
    client, settings, tmp_path, monkeypatch
):
    settings.MEDIA_ROOT = tmp_path
    member, profile = create_member_with_avatar(
        username="avatar-save-failure",
        avatar=image_upload(filename="current.png"),
    )
    old_name = profile.avatar.name
    old_path = stored_avatar_path(settings, profile)
    client.force_login(member)
    original_save = MemberProfile.save

    def fail_after_file_write(instance, *args, **kwargs):
        if instance.pk == profile.pk and not instance.avatar._committed:
            instance.avatar.save(instance.avatar.name, instance.avatar.file, save=False)
            raise IntegrityError("synthetic database failure")
        return original_save(instance, *args, **kwargs)

    monkeypatch.setattr(MemberProfile, "save", fail_after_file_write)

    with pytest.raises(IntegrityError, match="synthetic database failure"):
        client.post(
            reverse("members:profile_edit"),
            data=profile_data(avatar=image_upload(filename="failed.png")),
        )

    profile.refresh_from_db()
    assert profile.avatar.name == old_name
    assert old_path.exists()
    assert list(tmp_path.rglob("*.*")) == [old_path]


def test_profile_edit_shows_current_avatar_delete_control_and_privacy_notice(
    client, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"
    member, profile = create_member_with_avatar(
        username="avatar-interface",
        avatar=image_upload(filename="interface.png"),
    )
    client.force_login(member)

    response = client.get(reverse("members:profile_edit"))
    content = response.content.decode()

    assert response.status_code == 200
    assert profile.avatar.url in content
    assert 'name="remove_avatar"' in content
    assert 'class="avatar-preview"' in content
    assert 'class="avatar-editor avatar-editor--current"' in content
    assert 'aria-describedby="avatar-privacy-help"' in content
    assert (
        "Uploaded images are stored as provided and may contain location, device or "
        "other metadata. Remove sensitive metadata before uploading."
    ) in content


def test_development_media_patterns_serve_local_files(settings, tmp_path):
    media_file = tmp_path / "member_avatars" / "served.png"
    media_file.parent.mkdir()
    media_file.write_bytes(image_bytes())

    with override_settings(DEBUG=True, MEDIA_URL="/media/", MEDIA_ROOT=tmp_path):
        patterns = development_media_urlpatterns()
        match = resolve("/media/member_avatars/served.png", urlconf=tuple(patterns))
        response = match.func(
            RequestFactory().get("/media/member_avatars/served.png"), **match.kwargs
        )

    assert response.status_code == 200
    assert b"".join(response.streaming_content) == media_file.read_bytes()


def test_production_urlconf_does_not_add_development_media_patterns():
    with override_settings(DEBUG=False, MEDIA_URL="/media/"):
        assert development_media_urlpatterns() == []


@pytest.mark.django_db
def test_avatar_is_stored_under_a_random_name(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    names = []
    for username in ("random-name-one", "random-name-two"):
        _member, profile = create_member_with_avatar(
            username=username,
            avatar=image_upload(filename="Casey_Nguyen.png"),
        )
        names.append(profile.avatar.name)
        assert re.fullmatch(r"member_avatars/[0-9a-f]{32}\.png", profile.avatar.name)
        assert Path(tmp_path, profile.avatar.name).exists()

        profile.bio = "Saving again keeps the stored file."
        profile.save()
        assert profile.avatar.name == names[-1]

    assert names[0] != names[1]
