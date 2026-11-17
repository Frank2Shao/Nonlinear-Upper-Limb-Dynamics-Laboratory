import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.members.models import MemberProfile
from tests import factories

pytestmark = pytest.mark.django_db


def create_member(
    *,
    username: str,
    verified: bool = True,
    is_active: bool = True,
) -> tuple[User, MemberProfile]:
    return factories.create_member(
        username,
        verified=verified,
        user_fields={"is_active": is_active},
    )


def valid_profile_data(**overrides):
    data = {
        "display_name": "Updated Member",
        "bio": "Training with control and purpose.",
        "experience_level": MemberProfile.ExperienceLevel.ONE_TO_THREE_YEARS,
        "preferred_arm": MemberProfile.PreferredArm.BOTH,
        "instagram_handle": "updated.member",
        "other_social_url": "https://example.com/member",
    }
    data.update(overrides)
    return data


def test_anonymous_user_is_redirected_to_login(client):
    response = client.get(reverse("members:profile_edit"))

    assert response.status_code == 302
    assert response.url == (
        f"{reverse('account_login')}?next={reverse('members:profile_edit')}"
    )


def test_unverified_user_cannot_access_profile_edit(client):
    user, _profile = create_member(username="unverified-profile", verified=False)
    client.force_login(user)

    response = client.get(reverse("members:profile_edit"))

    assert response.status_code == 403


def test_inactive_user_cannot_access_profile_edit(client):
    user, _profile = create_member(username="inactive-profile", is_active=False)
    client.force_login(user)

    response = client.get(reverse("members:profile_edit"))

    assert response.status_code == 302
    assert response.url == (
        f"{reverse('account_login')}?next={reverse('members:profile_edit')}"
    )


def test_verified_member_sees_only_their_profile(client):
    member, profile = create_member(username="profile-owner")
    other, other_profile = create_member(username="other-profile-owner")
    profile.display_name = "Profile Owner"
    profile.save()
    other_profile.display_name = "Private Other Member"
    other_profile.save()
    client.force_login(member)

    response = client.get(reverse("members:profile_edit"))
    content = response.content.decode()

    assert response.status_code == 200
    assert response.context["profile"] == profile
    assert "Profile Owner" in content
    assert "Private Other Member" not in content
    assert other.username not in content


def test_member_can_save_allowed_profile_fields(client):
    member, profile = create_member(username="profile-save")
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=valid_profile_data(instagram_handle="@updated.member"),
    )

    assert response.status_code == 302
    assert response.url == reverse("account")
    profile.refresh_from_db()
    assert profile.display_name == "Updated Member"
    assert profile.bio == "Training with control and purpose."
    assert profile.experience_level == MemberProfile.ExperienceLevel.ONE_TO_THREE_YEARS
    assert profile.preferred_arm == MemberProfile.PreferredArm.BOTH
    assert profile.instagram_handle == "updated.member"
    assert profile.other_social_url == "https://example.com/member"

    follow_up = client.get(response.url)
    assert "Your profile has been updated." in follow_up.content.decode()


def test_profile_save_does_not_change_publication_or_admin_fields(client):
    member, profile = create_member(username="profile-protected")
    profile.is_published = True
    profile.is_hidden_by_admin = True
    profile.executive_role = "President"
    profile.save()
    other, other_profile = create_member(username="forged-target")
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=valid_profile_data(
            user=other.pk,
            is_published=False,
            is_hidden_by_admin=False,
            executive_role="Changed",
            created_at="2000-01-01T00:00:00Z",
            updated_at="2000-01-01T00:00:00Z",
        ),
    )

    assert response.status_code == 302
    profile.refresh_from_db()
    other_profile.refresh_from_db()
    assert profile.user == member
    assert profile.is_published is True
    assert profile.is_hidden_by_admin is True
    assert profile.executive_role == "President"
    assert other_profile.display_name is None


def test_duplicate_display_name_returns_bound_form_error(client):
    _existing_user, existing_profile = create_member(username="existing-name")
    existing_profile.display_name = "Shared Name"
    existing_profile.save()
    member, profile = create_member(username="duplicate-name")
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=valid_profile_data(display_name="shared name"),
    )

    assert response.status_code == 200
    assert response.context["form"].errors["display_name"]
    assert response.context["form"].data["display_name"] == "shared name"
    profile.refresh_from_db()
    assert profile.display_name is None


def test_bio_html_is_rejected_without_losing_input(client):
    member, profile = create_member(username="profile-html")
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=valid_profile_data(bio="<strong>Unsafe biography</strong>"),
    )

    assert response.status_code == 200
    assert response.context["form"].errors["bio"] == [
        "Bio must contain plain text only."
    ]
    assert "Unsafe biography" in response.content.decode()
    profile.refresh_from_db()
    assert profile.bio is None


def test_instagram_and_social_url_validation_errors_are_displayed(client):
    member, profile = create_member(username="profile-social")
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=valid_profile_data(
            instagram_handle="not a username",
            other_social_url="http://example.com/insecure",
        ),
    )

    assert response.status_code == 200
    form = response.context["form"]
    assert form.errors["instagram_handle"]
    assert form.errors["other_social_url"]
    profile.refresh_from_db()
    assert profile.instagram_handle is None
    assert profile.other_social_url is None


def test_account_page_links_to_profile_edit(client):
    member, _profile = create_member(username="account-profile-link")
    client.force_login(member)

    response = client.get(reverse("account"))

    assert response.status_code == 200
    assert reverse("members:profile_edit") in response.content.decode()


def test_profile_edit_uses_plain_post_without_javascript(client):
    member, profile = create_member(username="profile-no-js")
    client.force_login(member)

    response = client.post(
        reverse("members:profile_edit"),
        data=valid_profile_data(display_name="No JavaScript Member"),
        follow=True,
    )

    assert response.status_code == 200
    assert response.redirect_chain == [(reverse("account"), 302)]
    profile.refresh_from_db()
    assert profile.display_name == "No JavaScript Member"
