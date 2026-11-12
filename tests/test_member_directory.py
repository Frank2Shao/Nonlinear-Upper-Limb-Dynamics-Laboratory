import pytest
from allauth.account.models import EmailAddress
from django.urls import reverse

from apps.accounts.models import User
from apps.members.models import MemberProfile

pytestmark = pytest.mark.django_db


def create_profile(
    *,
    username: str,
    display_name: str | None = None,
    is_published: bool = True,
    is_hidden_by_admin: bool = False,
    is_active: bool = True,
    is_verified: bool = True,
    usu_id: str | None = None,
    **profile_fields,
) -> MemberProfile:
    user = User.objects.create_user(
        username=username,
        email=f"private-{username}@example.com",
        password="test-password",
        is_active=is_active,
        is_usyd_student=usu_id is not None,
        usu_id=usu_id,
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        primary=True,
        verified=is_verified,
    )
    return MemberProfile.objects.create(
        user=user,
        display_name=display_name,
        is_published=is_published,
        is_hidden_by_admin=is_hidden_by_admin,
        **profile_fields,
    )


def test_directory_is_public_and_uses_members_template(client):
    response = client.get(reverse("members:list"))

    assert response.status_code == 200
    assert "members/member_list.html" in [
        template.name for template in response.templates
    ]
    assert (
        "<title>Members | NULDL Armwrestling Club</title>" in response.content.decode()
    )


def test_directory_uses_public_queryset_and_excludes_ineligible_profiles(client):
    visible = create_profile(username="visible-member", display_name="Visible Member")
    create_profile(username="unpublished-member", is_published=False)
    create_profile(username="hidden-member", is_hidden_by_admin=True)
    create_profile(username="inactive-member", is_active=False)
    create_profile(username="unverified-member", is_verified=False)

    response = client.get(reverse("members:list"))

    assert list(response.context["profiles"]) == [visible]
    content = response.content.decode()
    assert "Visible Member" in content
    for excluded_name in (
        "unpublished-member",
        "hidden-member",
        "inactive-member",
        "unverified-member",
    ):
        assert excluded_name not in content


def test_directory_sorts_by_resolved_name_case_insensitively_and_stably(client):
    charlie = create_profile(username="charlie", display_name="charlie")
    alpha = create_profile(username="alpha")
    bravo_fallback = create_profile(username="Bravo")
    bravo_named = create_profile(username="bravo-named", display_name="bravo")

    response = client.get(reverse("members:list"))

    assert list(response.context["profiles"]) == [
        alpha,
        bravo_fallback,
        bravo_named,
        charlie,
    ]


def test_directory_cards_show_only_allowed_summary_fields(client):
    create_profile(
        username="summary-member",
        display_name="Summary Member",
        usu_id="00112233",
        experience_level=MemberProfile.ExperienceLevel.ONE_TO_THREE_YEARS,
        preferred_arm=MemberProfile.PreferredArm.BOTH,
        bio="PRIVATE BIO SENTINEL",
        instagram_handle="private.instagram",
        other_social_url="https://example.com/private-social",
        executive_role="PRIVATE EXECUTIVE SENTINEL",
    )

    response = client.get(reverse("members:list"))

    content = response.content.decode()
    assert "Summary Member" in content
    assert "1–3 years" in content
    assert "Both" in content
    for private_value in (
        "private-summary-member@example.com",
        "00112233",
        "PRIVATE BIO SENTINEL",
        "private.instagram",
        "https://example.com/private-social",
        "PRIVATE EXECUTIVE SENTINEL",
        "pending",
        "USYD",
        "USU ID",
    ):
        assert private_value not in content
    assert f'href="{reverse("members:detail", args=["summary-member"])}"' in content


def test_directory_uses_username_fallback_and_hides_not_specified_values(client):
    create_profile(username="fallback-member")

    response = client.get(reverse("members:list"))

    content = response.content.decode()
    assert "fallback-member" in content
    assert "Not specified" not in content
    assert "Experience level" not in content
    assert "Preferred arm" not in content
    assert 'class="member-card__avatar-fallback"' in content


def test_directory_has_clear_empty_state(client):
    response = client.get(reverse("members:list"))

    content = response.content.decode()
    assert "No public member profiles yet" in content
    assert (
        "Members can choose to publish their profiles after previewing them." in content
    )


@pytest.mark.parametrize("authenticated", [False, True])
def test_members_navigation_is_available_and_current(client, authenticated):
    if authenticated:
        profile = create_profile(username="navigation-member")
        client.force_login(profile.user)

    response = client.get(reverse("members:list"))

    content = response.content.decode()
    assert f'href="{reverse("members:list")}" aria-current="page"' in content
    assert ">Members</a>" in content
