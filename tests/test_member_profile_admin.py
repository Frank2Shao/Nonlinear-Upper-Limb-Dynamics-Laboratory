import pytest
from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from apps.accounts.models import User
from apps.members.admin import MemberProfileAdmin
from apps.members.models import MemberProfile

pytestmark = pytest.mark.django_db
PASSWORD = "A-valid-password-2026"


def create_user(*, username: str, **extra_fields) -> User:
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password=PASSWORD,
        **extra_fields,
    )


def create_profile(*, username: str = "profile-member") -> tuple[User, MemberProfile]:
    user = create_user(username=username)
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        primary=True,
        verified=True,
    )
    profile = MemberProfile.objects.create(
        user=user,
        display_name="Member Authored Name",
        bio="Member-authored biography",
        experience_level=MemberProfile.ExperienceLevel.ONE_TO_THREE_YEARS,
        preferred_arm=MemberProfile.PreferredArm.RIGHT,
        instagram_handle="member.profile",
        other_social_url="https://example.com/member",
        is_published=True,
    )
    return user, profile


def grant_change_permission(user: User) -> User:
    user.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="members",
            codename="change_memberprofile",
        )
    )
    return user


def change_url(profile: MemberProfile) -> str:
    return reverse("admin:members_memberprofile_change", args=(profile.pk,))


def post_admin_change(
    client,
    profile: MemberProfile,
    *,
    is_hidden: bool,
    executive_role: str = "",
    **forged_fields,
):
    data = {
        "executive_role": executive_role,
        "_save": "Save",
        **forged_fields,
    }
    if is_hidden:
        data["is_hidden_by_admin"] = "on"
    return client.post(change_url(profile), data=data)


def test_admin_configuration_uses_standard_permission_without_custom_actions():
    model_admin = admin.site._registry[MemberProfile]

    assert isinstance(model_admin, MemberProfileAdmin)
    assert model_admin.actions == ()
    assert not MemberProfile._meta.permissions


def test_regular_member_cannot_access_member_profile_admin(client):
    member, profile = create_profile(username="ordinary-profile-member")
    client.force_login(member)

    changelist_response = client.get(reverse("admin:members_memberprofile_changelist"))
    change_response = client.get(change_url(profile))

    assert changelist_response.status_code == 302
    assert reverse("admin:login") in changelist_response.url
    assert change_response.status_code == 302
    assert reverse("admin:login") in change_response.url


def test_staff_without_change_permission_cannot_access_member_profile_admin(client):
    staff = create_user(username="unpermitted-profile-staff", is_staff=True)
    _member, profile = create_profile(username="protected-profile")
    client.force_login(staff)

    changelist_response = client.get(reverse("admin:members_memberprofile_changelist"))
    change_response = client.get(change_url(profile))

    assert changelist_response.status_code == 403
    assert change_response.status_code == 403


def test_authorized_staff_only_sees_admin_managed_fields_as_editable(client):
    staff = grant_change_permission(
        create_user(username="profile-change-staff", is_staff=True)
    )
    _member, profile = create_profile(username="readonly-profile")
    client.force_login(staff)

    response = client.get(change_url(profile))

    assert response.status_code == 200
    assert response.context["has_add_permission"] is False
    assert response.context["has_delete_permission"] is False
    assert set(response.context["adminform"].form.fields) == {
        "is_hidden_by_admin",
        "executive_role",
    }


def test_authorized_staff_can_hide_unhide_and_update_executive_role(client):
    staff = grant_change_permission(
        create_user(username="profile-state-staff", is_staff=True)
    )
    _member, profile = create_profile(username="profile-state-member")
    client.force_login(staff)

    hidden_response = post_admin_change(
        client,
        profile,
        is_hidden=True,
        executive_role="President",
    )
    profile.refresh_from_db()

    assert hidden_response.status_code == 302
    assert profile.is_hidden_by_admin is True
    assert profile.executive_role == "President"

    visible_response = post_admin_change(
        client,
        profile,
        is_hidden=False,
        executive_role="Vice President",
    )
    profile.refresh_from_db()

    assert visible_response.status_code == 302
    assert profile.is_hidden_by_admin is False
    assert profile.executive_role == "Vice President"


def test_admin_change_cannot_modify_member_authored_or_system_fields(client):
    staff = grant_change_permission(
        create_user(username="forged-profile-staff", is_staff=True)
    )
    member, profile = create_profile(username="forged-profile-member")
    replacement_user = create_user(username="replacement-profile-member")
    original_created_at = profile.created_at
    original_updated_at = profile.updated_at
    client.force_login(staff)

    response = post_admin_change(
        client,
        profile,
        is_hidden=True,
        executive_role="Captain",
        user=replacement_user.pk,
        display_name="Forged Name",
        bio="Forged biography",
        experience_level=MemberProfile.ExperienceLevel.OVER_THREE_YEARS,
        preferred_arm=MemberProfile.PreferredArm.LEFT,
        instagram_handle="forged.handle",
        other_social_url="https://example.com/forged",
        is_published="",
        created_at="2000-01-01T00:00:00Z",
        updated_at="2000-01-01T00:00:00Z",
    )
    profile.refresh_from_db()

    assert response.status_code == 302
    assert profile.user == member
    assert profile.display_name == "Member Authored Name"
    assert profile.bio == "Member-authored biography"
    assert profile.experience_level == MemberProfile.ExperienceLevel.ONE_TO_THREE_YEARS
    assert profile.preferred_arm == MemberProfile.PreferredArm.RIGHT
    assert profile.instagram_handle == "member.profile"
    assert profile.other_social_url == "https://example.com/member"
    assert profile.is_published is True
    assert profile.is_hidden_by_admin is True
    assert profile.executive_role == "Captain"
    assert profile.created_at == original_created_at
    assert profile.updated_at > original_updated_at


def test_superuser_can_manage_hidden_state_and_executive_role(client):
    superuser = User.objects.create_superuser(
        username="profile-superuser",
        email="profile-superuser@example.com",
        password=PASSWORD,
    )
    _member, profile = create_profile(username="superuser-managed-profile")
    client.force_login(superuser)

    response = post_admin_change(
        client,
        profile,
        is_hidden=True,
        executive_role="Secretary",
    )
    profile.refresh_from_db()

    assert response.status_code == 302
    assert profile.is_hidden_by_admin is True
    assert profile.executive_role == "Secretary"


def test_admin_change_creates_standard_django_log_entry(client):
    staff = grant_change_permission(
        create_user(username="logged-profile-staff", is_staff=True)
    )
    _member, profile = create_profile(username="logged-profile-member")
    client.force_login(staff)

    response = post_admin_change(client, profile, is_hidden=True)

    assert response.status_code == 302
    entry = LogEntry.objects.get(user=staff, object_id=str(profile.pk))
    assert entry.action_flag == CHANGE
    assert "Is hidden by admin" in entry.get_change_message()


def test_hiding_removes_profile_from_public_pages_without_changing_account(client):
    staff = grant_change_permission(
        create_user(username="visibility-profile-staff", is_staff=True)
    )
    member, profile = create_profile(username="visibility-profile-member")
    client.force_login(staff)

    response = post_admin_change(client, profile, is_hidden=True)
    profile.refresh_from_db()
    member.refresh_from_db()

    assert response.status_code == 302
    assert profile.is_published is True
    assert member.is_active is True
    assert MemberProfile.objects.public().filter(pk=profile.pk).exists() is False

    public_client = Client()
    assert (
        "Member Authored Name"
        not in public_client.get(reverse("members:list")).content.decode()
    )
    assert (
        public_client.get(
            reverse("members:detail", args=(member.username,))
        ).status_code
        == 404
    )

    client.force_login(member)
    assert client.get(reverse("members:profile_edit")).status_code == 200
    unpublish_response = client.post(reverse("members:profile_unpublish"))
    profile.refresh_from_db()

    assert unpublish_response.status_code == 302
    assert profile.is_published is False
    assert profile.is_hidden_by_admin is True
