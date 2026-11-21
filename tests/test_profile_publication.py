import re

import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.models import User
from apps.members.models import MemberProfile
from tests import factories

pytestmark = pytest.mark.django_db

PROFILE_ROUTES = (
    "members:profile_preview",
    "members:profile_publish",
    "members:profile_unpublish",
)


SECTION_PATTERN = re.compile(
    r'<span class="report-section__index" aria-hidden="true">(\d+)</span>\s*'
    r'<h2 id="[\w-]+">([^<]+)</h2>'
)


def div_block(content: str, marker: str) -> str:
    """The balanced <div> that starts at marker."""
    start = content.index(marker)
    start = content.rindex("<div", 0, start)
    depth = 0
    for match in re.finditer(r"<(/?)div\b[^>]*>", content[start:]):
        depth += -1 if match.group(1) else 1
        if depth == 0:
            return content[start : start + match.end()]
    raise AssertionError(f"Unbalanced block at {marker}")


def create_member(
    *,
    username: str,
    verified: bool = True,
    is_active: bool = True,
    is_published: bool = False,
    is_hidden_by_admin: bool = False,
) -> tuple[User, MemberProfile]:
    return factories.create_member(
        username,
        verified=verified,
        user_fields={"is_active": is_active},
        is_published=is_published,
        is_hidden_by_admin=is_hidden_by_admin,
    )


@pytest.mark.parametrize("route_name", PROFILE_ROUTES)
def test_anonymous_user_is_redirected_to_login(client, route_name):
    url = reverse(route_name)

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('account_login')}?next={url}"


@pytest.mark.parametrize("route_name", PROFILE_ROUTES)
def test_unverified_member_cannot_access_publication_flow(client, route_name):
    user, _profile = create_member(
        username=f"unverified-{route_name[-7:]}", verified=False
    )
    client.force_login(user)

    response = client.get(reverse(route_name))

    assert response.status_code == 403


def test_preview_uses_only_the_current_members_profile(client):
    member, profile = create_member(username="preview-owner")
    profile.display_name = "Current Preview"
    profile.bio = "Current member biography"
    profile.save()
    _other, other_profile = create_member(username="private-other")
    other_profile.display_name = "Other Private Profile"
    other_profile.bio = "Other private biography"
    other_profile.save()
    client.force_login(member)

    response = client.get(
        reverse("members:profile_preview"),
        {"profile": other_profile.pk, "user": other_profile.user_id},
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert response.context["profile"] == profile
    assert "Current Preview" in content
    assert "Current member biography" in content
    assert "Other Private Profile" not in content
    assert "Other private biography" not in content


def test_preview_shares_the_public_layout_one_heading_level_lower(client):
    member, profile = create_member(username="preview-layout")
    profile.display_name = "Preview Layout"
    profile.bio = "Preview biography"
    profile.instagram_handle = "preview.layout"
    profile.researcher_number = 12
    profile.save()
    client.force_login(member)

    content = client.get(reverse("members:profile_preview")).content.decode()
    levels = [
        (level, re.sub(r"<[^>]+>", "", text).strip())
        for level, text in re.findall(r"<h([1-6])[^>]*>(.*?)</h\1>", content, re.S)
    ]

    assert levels[:4] == [
        ("1", "Profile Preview"),
        ("2", "Preview Layout"),
        ("3", "Bio"),
        ("3", "Links"),
    ]
    assert '<p class="gold-tag">Researcher 12</p>' in content
    assert 'class="profile-panel"' in content


def test_unpublished_profile_can_be_previewed_without_changing_state(client):
    member, profile = create_member(username="unpublished-preview")
    client.force_login(member)

    response = client.get(reverse("members:profile_preview"))

    assert response.status_code == 200
    assert "Publish profile" in response.content.decode()
    profile.refresh_from_db()
    assert profile.is_published is False


@pytest.mark.parametrize(
    "route_name,initial_state",
    (("members:profile_publish", False), ("members:profile_unpublish", True)),
)
def test_confirmation_get_never_changes_publication_state(
    client, route_name, initial_state
):
    member, profile = create_member(
        username=f"get-state-{initial_state}",
        is_published=initial_state,
    )
    client.force_login(member)

    response = client.get(reverse(route_name))

    assert response.status_code == 200
    profile.refresh_from_db()
    assert profile.is_published is initial_state


def test_publish_post_is_idempotent_and_uses_fixed_redirect(client):
    member, profile = create_member(username="publish-member")
    client.force_login(member)
    url = reverse("members:profile_publish")

    first = client.post(f"{url}?next=https://example.invalid/redirect")
    second = client.post(url)

    assert first.status_code == 302
    assert first.url == reverse("members:profile_preview")
    assert second.status_code == 302
    assert second.url == reverse("members:profile_preview")
    profile.refresh_from_db()
    assert profile.is_published is True


def test_unpublish_post_is_idempotent_and_uses_fixed_redirect(client):
    member, profile = create_member(
        username="unpublish-member",
        is_published=True,
    )
    client.force_login(member)
    url = reverse("members:profile_unpublish")

    first = client.post(f"{url}?next=https://example.invalid/redirect")
    second = client.post(url)

    assert first.status_code == 302
    assert first.url == reverse("members:profile_preview")
    assert second.status_code == 302
    assert second.url == reverse("members:profile_preview")
    profile.refresh_from_db()
    assert profile.is_published is False


@pytest.mark.parametrize(
    "route_name",
    ("members:profile_publish", "members:profile_unpublish"),
)
def test_publication_posts_require_csrf(route_name):
    member, profile = create_member(
        username=f"csrf-{route_name[-7:]}",
        is_published=route_name.endswith("unpublish"),
    )
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(member)

    response = csrf_client.post(reverse(route_name))

    assert response.status_code == 403
    profile.refresh_from_db()
    assert profile.is_published is route_name.endswith("unpublish")


def test_hidden_profile_can_publish_without_clearing_hidden_state(client):
    member, profile = create_member(
        username="hidden-publish",
        is_hidden_by_admin=True,
    )
    client.force_login(member)

    confirmation = client.get(reverse("members:profile_publish"))
    response = client.post(reverse("members:profile_publish"))

    assert confirmation.status_code == 200
    content = confirmation.content.decode()
    assert "currently unavailable on public pages" in content
    assert "administrator" not in content.lower()
    response_content = client.get(response.url).content.decode()
    assert "currently unavailable on public pages" in response_content
    profile.refresh_from_db()
    assert profile.is_published is True
    assert profile.is_hidden_by_admin is True
    assert MemberProfile.objects.public().filter(pk=profile.pk).exists() is False


def test_inactive_member_cannot_change_publication_state(client):
    member, profile = create_member(
        username="inactive-publication",
        is_active=False,
    )
    client.force_login(member)

    response = client.post(reverse("members:profile_publish"))

    assert response.status_code == 302
    profile.refresh_from_db()
    assert profile.is_published is False


def test_publish_confirmation_explains_public_fields_and_username_fallback(client):
    member, _profile = create_member(username="public-url-member")
    client.force_login(member)

    response = client.get(reverse("members:profile_publish"))
    content = response.content.decode()

    assert response.status_code == 200
    for label in (
        "Display name",
        "Username",
        "Avatar",
        "Experience level",
        "Preferred arm",
        "Bio",
        "Instagram Username",
        "Other HTTPS social URL",
    ):
        assert label in content
    assert "/members/public-url-member/" in content
    assert "It is also your public name because no Display name is set" in content
    assert "location, device or other metadata" in content
    assert "Researcher number, if one has been assigned" in content


def test_publish_confirmation_names_the_assigned_researcher_number(client):
    member, profile = create_member(username="numbered-publisher")
    profile.researcher_number = 7
    profile.save()
    client.force_login(member)

    content = client.get(reverse("members:profile_publish")).content.decode()

    assert "Researcher number (Researcher 07)" in content
    assert "if one has been assigned" not in content


@pytest.mark.parametrize(
    "route_name",
    ("members:profile_preview", "members:profile_publish"),
)
def test_preview_and_confirmation_exclude_private_and_admin_fields(client, route_name):
    member, profile = create_member(username="privacy-member")
    member.is_usyd_student = True
    member.usu_id = "001234567"
    member.usu_review_status = User.UsuReviewStatus.PENDING
    member.save()
    profile.display_name = "Public Profile Name"
    profile.executive_role = "Private Executive Role"
    profile.save()
    client.force_login(member)

    response = client.get(reverse(route_name))
    content = response.content.decode()

    assert response.status_code == 200
    assert member.email not in content
    assert member.usu_id not in content
    assert "USYD" not in content
    assert "Pending" not in content
    assert "Private Executive Role" not in content
    assert "Executive role" not in content


def test_profile_edit_links_to_preview(client):
    member, _profile = create_member(username="edit-preview-link")
    client.force_login(member)

    response = client.get(reverse("members:profile_edit"))

    assert response.status_code == 200
    assert reverse("members:profile_preview") in response.content.decode()


def test_profile_preview_links_back_to_account(client):
    member, _profile = create_member(username="preview-account-link")
    client.force_login(member)

    response = client.get(reverse("members:profile_preview"))

    content = response.content.decode()
    assert response.status_code == 200
    assert "Back to Account" in content
    assert reverse("account") in content


def test_publish_confirmation_uses_numbered_sections_and_a_facts_table(client):
    member, profile = create_member(username="publish-layout")
    profile.display_name = "Publish Layout"
    profile.save()
    client.force_login(member)

    content = client.get(reverse("members:profile_publish")).content.decode()

    assert '<p class="label-mono">Publication confirmation</p>' in content
    assert SECTION_PATTERN.findall(content) == [
        ("01", "What becomes public"),
        ("02", "Your public page"),
    ]
    rules = content.split('<ul class="rule-list">')[1].split("</ul>")[0]
    assert rules.count("<li>") == 8
    assert "<dt>Public name</dt><dd>Publish Layout</dd>" in content
    assert (
        "<dt>Profile URL</dt><dd><code>/members/publish-layout/</code></dd>" in content
    )
    assert "Your Username is always part of your public profile URL." in content
    assert "because no Display name is set" not in content
    assert content.index("Your public page") < content.index("Publish profile</button>")


def test_unpublish_confirmation_shows_the_public_page_table(client):
    member, _profile = create_member(username="unpublish-layout", is_published=True)
    client.force_login(member)

    content = client.get(reverse("members:profile_unpublish")).content.decode()

    assert '<p class="label-mono">Publication confirmation</p>' in content
    assert SECTION_PATTERN.findall(content) == [("01", "Your public page")]
    assert "<dt>Public name</dt><dd>unpublish-layout</dd>" in content
    assert (
        "<dt>Profile URL</dt><dd><code>/members/unpublish-layout/</code></dd>"
        in content
    )
    assert content.index("Your public page") < content.index(
        "Unpublish profile</button>"
    )


def test_preview_frames_the_public_component_and_keeps_notice_and_actions_outside(
    client,
):
    member, _profile = create_member(
        username="preview-frame", is_published=True, is_hidden_by_admin=True
    )
    client.force_login(member)

    content = client.get(reverse("members:profile_preview")).content.decode()
    frame = div_block(content, 'class="preview-frame"')

    assert '<p class="label-mono">Private preview</p>' in content
    assert "<span>Public view</span>" in frame
    assert "<span>/members/preview-frame/</span>" in frame
    assert 'class="profile-panel"' in frame
    assert "currently unavailable on public pages" not in frame
    assert "Back to Account" not in frame
    assert "Unpublish profile" not in frame
    assert content.index("currently unavailable on public pages") < content.index(frame)
    assert content.index(frame) < content.index("Back to Account")
