import re

import pytest
from django.urls import reverse

from apps.members.models import MemberProfile
from tests.factories import create_member
from tests.privacy import assert_no_private_values

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
    return create_member(
        username,
        email=f"private-{username}@example.com",
        verified=is_verified,
        user_fields={
            "is_active": is_active,
            "is_usyd_student": True,
            "usu_id": "00112233",
        },
        is_published=is_published,
        is_hidden_by_admin=is_hidden_by_admin,
        executive_role="PRIVATE EXECUTIVE SENTINEL",
        **profile_fields,
    )[1]


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
    assert_no_private_values(
        content,
        (
            "private-public-detail@example.com",
            "00112233",
            "PRIVATE EXECUTIVE SENTINEL",
            "pending",
            "USYD",
            "USU ID",
            profile.created_at,
            profile.updated_at,
        ),
        context="Member detail",
    )


def headings(content: str) -> list[tuple[str, str]]:
    return [
        (level, re.sub(r"<[^>]+>", "", text).strip())
        for level, text in re.findall(r"<h([1-6])[^>]*>(.*?)</h\1>", content, re.S)
    ]


def test_detail_has_back_link_panel_and_numbered_sections(client):
    profile = create_profile(
        username="layout-detail",
        display_name="Layout Member",
        bio="A short public bio.",
        instagram_handle="layout.member",
        researcher_number=7,
    )

    content = client.get(
        reverse("members:detail", args=[profile.user.username])
    ).content.decode()

    assert (
        f'<a class="back-link" href="{reverse("members:list")}">'
        '<span aria-hidden="true">←</span> Back to members</a>'
    ) in content
    assert headings(content) == [("1", "Layout Member"), ("2", "Bio"), ("2", "Links")]
    kicker = re.search(r'<div class="profile-kicker">(.*?)</div>', content, re.S).group(
        1
    )
    assert '<p class="label-mono">Member profile</p>' in kicker
    assert '<p class="gold-tag">Researcher 07</p>' in kicker
    assert content.index("Researcher 07") < content.index("<h1")
    assert re.findall(r'report-section__index" aria-hidden="true">(\d+)<', content) == [
        "01",
        "02",
    ]


def test_detail_leaves_out_empty_sections_and_unassigned_tag(client):
    links_only = create_profile(
        username="links-only",
        display_name="Links Only",
        instagram_handle="links.only",
    )
    bare = create_profile(username="bare-detail", display_name="Bare Member")

    links_content = client.get(
        reverse("members:detail", args=[links_only.user.username])
    ).content.decode()
    bare_content = client.get(
        reverse("members:detail", args=[bare.user.username])
    ).content.decode()

    assert headings(links_content) == [("1", "Links Only"), ("2", "Links")]
    assert re.findall(
        r'report-section__index" aria-hidden="true">(\d+)<', links_content
    ) == ["01"]
    assert "Researcher" not in links_content
    assert "gold-tag" not in links_content
    assert headings(bare_content) == [("1", "Bare Member")]
    assert "report-section" not in bare_content


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
