import re

import pytest
from allauth.account.models import EmailAddress
from django.urls import reverse

from apps.accounts.models import User
from apps.members.models import MemberProfile

pytestmark = pytest.mark.django_db


def create_profile(
    *,
    username: str,
    is_published: bool = True,
    is_hidden_by_admin: bool = False,
    is_active: bool = True,
    is_verified: bool = True,
    **profile_fields,
) -> MemberProfile:
    user = User.objects.create_user(
        username=username,
        email=f"private-{username}@example.com",
        password="test-password",
        is_active=is_active,
        is_usyd_student=True,
        usu_id="00112233",
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        primary=True,
        verified=is_verified,
    )
    return MemberProfile.objects.create(
        user=user,
        is_published=is_published,
        is_hidden_by_admin=is_hidden_by_admin,
        executive_role="PRIVATE EXECUTIVE SENTINEL",
        **profile_fields,
    )


def test_detail_uses_exact_username_url_and_public_template(client):
    profile = create_profile(username="CaseSensitiveMember", display_name="Case Member")
    path = reverse("members:detail", args=[profile.user.username])

    response = client.get(path)

    assert response.status_code == 200
    assert response.context["profile"] == profile
    assert "members/member_detail.html" in [
        template.name for template in response.templates
    ]
    content = response.content.decode()
    assert "<title>Case Member | Members | NULDL Armwrestling Club</title>" in content
    assert '<meta name="robots" content="index, follow">' in content
    assert f'href="{reverse("members:list")}" aria-current="page"' in content
    assert client.get(path.lower()).status_code == 404


def test_detail_shows_only_allowed_public_fields_and_safe_external_links(client):
    profile = create_profile(
        username="public-detail",
        display_name="Public Member",
        experience_level=MemberProfile.ExperienceLevel.ONE_TO_THREE_YEARS,
        preferred_arm=MemberProfile.PreferredArm.BOTH,
        bio="First line\nSecond line",
        instagram_handle="public.member",
        other_social_url="https://example.com/member?from=club&view=public",
    )

    response = client.get(reverse("members:detail", args=[profile.user.username]))

    content = response.content.decode()
    for public_value in (
        "Public Member",
        "@public-detail",
        "1–3 years",
        "Both",
        "First line<br>Second line",
        "Instagram: @public.member",
        "Other social profile",
    ):
        assert public_value in content
    assert (
        'href="https://www.instagram.com/public.member/" target="_blank" '
        'rel="noopener noreferrer"' in content
    )
    assert (
        'href="https://example.com/member?from=club&amp;view=public" '
        'target="_blank" rel="noopener noreferrer"' in content
    )
    for private_value in (
        "private-public-detail@example.com",
        "00112233",
        "PRIVATE EXECUTIVE SENTINEL",
        "pending",
        "USYD",
        "USU ID",
        str(profile.created_at),
        str(profile.updated_at),
    ):
        assert private_value not in content


def test_detail_escapes_profile_content(client):
    profile = create_profile(username="escaped-detail", display_name="Escaped Member")
    MemberProfile.objects.filter(pk=profile.pk).update(
        bio='<script>alert("profile")</script>',
    )

    content = client.get(
        reverse("members:detail", args=[profile.user.username])
    ).content.decode()

    assert '<script>alert("profile")</script>' not in content
    assert "&lt;script&gt;alert(&quot;profile&quot;)&lt;/script&gt;" in content


def test_detail_hides_not_specified_values(client):
    profile = create_profile(username="unspecified-detail")

    content = client.get(
        reverse("members:detail", args=[profile.user.username])
    ).content.decode()

    assert "Not specified" not in content
    assert "Experience level" not in content
    assert "Preferred arm" not in content


def test_all_invisible_and_missing_profiles_return_the_same_404(client):
    profiles = (
        create_profile(username="unpublished-detail", is_published=False),
        create_profile(username="hidden-detail", is_hidden_by_admin=True),
        create_profile(username="inactive-detail", is_active=False),
        create_profile(username="unverified-detail", is_verified=False),
    )
    paths = [
        reverse("members:detail", args=[profile.user.username]) for profile in profiles
    ]
    paths.append(reverse("members:detail", args=["missing-detail"]))

    responses = [client.get(path) for path in paths]

    assert {response.status_code for response in responses} == {404}
    response_bodies = {
        re.search(
            r"<main\b.*?</main>",
            response.content.decode(),
            flags=re.DOTALL,
        ).group()
        for response in responses
    }
    assert len(response_bodies) == 1
    content = next(iter(response_bodies))
    for profile in profiles:
        assert profile.user.username not in content
