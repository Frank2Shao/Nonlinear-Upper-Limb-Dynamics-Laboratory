import re

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.services import review_usu_id
from apps.members.models import MemberProfile
from tests import factories

User = get_user_model()
PASSWORD = "A-valid-password-2026"
pytestmark = pytest.mark.django_db


def create_user(*, username: str, verified: bool = True, **extra_fields):
    return factories.create_user(
        username,
        email=f"{username}@example.net",
        password=PASSWORD,
        verified=verified,
        **extra_fields,
    )


def test_anonymous_user_is_redirected_to_login(client):
    response = client.get(reverse("account"))

    assert response.status_code == 302
    assert response.url == f"{reverse('account_login')}?next={reverse('account')}"


def test_member_sees_only_their_account_information(client):
    member = create_user(username="account_member")
    other = create_user(username="other_member")
    client.force_login(member)

    response = client.get(reverse("account"))

    assert response.status_code == 200
    content = response.content.decode()
    assert member.username in content
    assert member.email in content
    assert other.username not in content
    assert other.email not in content
    assert "Verified" in content


def test_account_page_reports_unverified_email_status(client):
    member = create_user(username="unverified_status", verified=False)
    client.force_login(member)

    response = client.get(reverse("account"))

    assert response.status_code == 200
    assert "Not verified" in response.content.decode()


def test_account_form_is_initialized_from_the_current_member(client):
    member = create_user(
        username="existing_identity",
        is_usyd_student=True,
        usu_id="00112233",
    )
    client.force_login(member)

    response = client.get(reverse("account"))

    assert response.status_code == 200
    assert response.context["form"].initial == {
        "is_usyd_student": True,
        "usu_id": "00112233",
    }


def test_member_can_submit_numeric_usu_id_and_preserve_leading_zeroes(client):
    member = create_user(username="numeric_account")
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={"is_usyd_student": "on", "usu_id": " 00123456 "},
    )

    assert response.status_code == 302
    assert response.url == reverse("account")
    member.refresh_from_db()
    assert member.is_usyd_student
    assert member.usu_id == "00123456"
    assert member.usu_review_status == User.UsuReviewStatus.PENDING


def test_non_usyd_member_cannot_submit_usu_id(client):
    member = create_user(username="non_usyd_account")
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={"usu_id": "12345678"},
    )

    assert response.status_code == 200
    assert "USU ID is only available to USYD students." in response.content.decode()
    member.refresh_from_db()
    assert not member.is_usyd_student
    assert member.usu_id is None


def test_account_rejects_non_numeric_usu_id(client):
    member = create_user(username="invalid_usu_account")
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={"is_usyd_student": "on", "usu_id": "1234A678"},
    )

    assert response.status_code == 200
    assert "USU ID must contain digits only." in response.content.decode()
    member.refresh_from_db()
    assert member.usu_id is None


def test_changing_reviewed_usu_id_returns_status_to_pending(client):
    reviewer = create_user(
        username="account_reviewer",
        is_staff=True,
        can_review_usu_id=True,
    )
    member = create_user(
        username="reviewed_account",
        is_usyd_student=True,
        usu_id="11111111",
    )
    member = review_usu_id(
        user=member,
        reviewer=reviewer,
        status=User.UsuReviewStatus.VERIFIED,
    )
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={"is_usyd_student": "on", "usu_id": "22222222"},
    )

    assert response.status_code == 302
    member.refresh_from_db()
    assert member.usu_id == "22222222"
    assert member.usu_review_status == User.UsuReviewStatus.PENDING
    assert member.usu_reviewed_at is None
    assert member.usu_reviewed_by is None


def test_clearing_usyd_declaration_clears_identity_and_review(client):
    reviewer = create_user(
        username="clear_account_reviewer",
        is_staff=True,
        can_review_usu_id=True,
    )
    member = create_user(
        username="clear_account",
        is_usyd_student=True,
        usu_id="12345678",
    )
    member = review_usu_id(
        user=member,
        reviewer=reviewer,
        status=User.UsuReviewStatus.REJECTED,
    )
    client.force_login(member)

    response = client.post(reverse("account"), data={"usu_id": ""})

    assert response.status_code == 302
    member.refresh_from_db()
    assert not member.is_usyd_student
    assert member.usu_id is None
    assert member.usu_review_status == User.UsuReviewStatus.NOT_SUBMITTED
    assert member.usu_reviewed_at is None
    assert member.usu_reviewed_by is None


def test_forged_read_only_and_review_fields_are_ignored(client):
    reviewer = create_user(username="forged_reviewer", is_staff=True)
    member = create_user(username="forged_account")
    original_username = member.username
    original_email = member.email
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={
            "username": "replaced_username",
            "email": "replaced@example.net",
            "is_usyd_student": "on",
            "usu_id": "87654321",
            "usu_review_status": User.UsuReviewStatus.VERIFIED,
            "usu_reviewed_at": "2026-10-24T12:00:00Z",
            "usu_reviewed_by": reviewer.pk,
        },
    )

    assert response.status_code == 302
    member.refresh_from_db()
    assert member.username == original_username
    assert member.email == original_email
    assert member.usu_id == "87654321"
    assert member.usu_review_status == User.UsuReviewStatus.PENDING
    assert member.usu_reviewed_at is None
    assert member.usu_reviewed_by is None


def test_member_update_cannot_modify_another_user(client):
    member = create_user(username="editing_member")
    other = create_user(
        username="protected_member",
        is_usyd_student=True,
        usu_id="11112222",
    )
    client.force_login(member)

    response = client.post(
        reverse("account"),
        data={
            "user": other.pk,
            "is_usyd_student": "on",
            "usu_id": "99998888",
        },
    )

    assert response.status_code == 302
    member.refresh_from_db()
    other.refresh_from_db()
    assert member.usu_id == "99998888"
    assert other.usu_id == "11112222"


def test_account_page_links_password_change_and_uses_post_logout(client):
    member = create_user(username="account_actions")
    client.force_login(member)

    response = client.get(reverse("account"))
    content = response.content.decode()

    assert reverse("account_change_password") in content
    assert f'action="{reverse("account_logout")}"' in content
    assert '<form method="post"' in content


def test_account_details_include_profile_summary_and_publication_guidance(client):
    member = create_user(username="account_profile_summary")
    profile = MemberProfile.objects.create(
        user=member,
        display_name="Account Profile Member",
        bio="A synthetic account profile biography.",
        experience_level=MemberProfile.ExperienceLevel.ONE_TO_THREE_YEARS,
        preferred_arm=MemberProfile.PreferredArm.BOTH,
        instagram_handle="account.profile",
        other_social_url="https://example.com/account-profile",
    )
    client.force_login(member)

    response = client.get(reverse("account"))

    content = response.content.decode()
    assert response.context["member_profile"] == profile
    assert '<h2 id="account-profile-title">Public member profile</h2>' in content
    assert "Your username is always part of your public profile URL." in content
    assert "Leave optional text fields blank" in content
    for value in (
        "Account Profile Member",
        "A synthetic account profile biography.",
        "1–3 years",
        "Both",
        "account.profile",
        "https://example.com/account-profile",
        "Not published",
    ):
        assert value in content


@pytest.mark.parametrize(
    ("is_published", "is_hidden_by_admin", "status", "action_name", "route_name"),
    (
        (False, False, "Not published", "Publish profile", "members:profile_publish"),
        (True, False, "Published", "Unpublish profile", "members:profile_unpublish"),
        (
            True,
            True,
            "Unavailable on public pages",
            "Unpublish profile",
            "members:profile_unpublish",
        ),
    ),
)
def test_account_profile_actions_follow_publication_state(
    client,
    is_published,
    is_hidden_by_admin,
    status,
    action_name,
    route_name,
):
    member = create_user(username=f"account_profile_{status.replace(' ', '_')}")
    MemberProfile.objects.create(
        user=member,
        is_published=is_published,
        is_hidden_by_admin=is_hidden_by_admin,
    )
    client.force_login(member)

    response = client.get(reverse("account"))

    content = response.content.decode()
    assert status in content
    assert action_name in content
    assert reverse(route_name) in content
    assert reverse("members:profile_edit") in content
    assert reverse("members:profile_preview") in content


def section_titles(content: str) -> list[tuple[str, str]]:
    """(index, title) of every numbered report section, in page order."""
    return re.findall(
        r'<span class="report-section__index" aria-hidden="true">(\d+)</span>\s*'
        r'<h2 id="[\w-]+">([^<]+)</h2>',
        content,
    )


def test_account_page_uses_a_heading_and_four_numbered_sections(client):
    member = create_user(username="account_sections")
    MemberProfile.objects.create(user=member)
    client.force_login(member)

    content = client.get(reverse("account")).content.decode()

    assert '<p class="label-mono">Member settings</p>' in content
    assert '<h1 id="account-title">Account</h1>' in content
    assert section_titles(content) == [
        ("01", "Account details"),
        ("02", "Public member profile"),
        ("03", "USYD and USU details"),
        ("04", "Security"),
    ]
    assert content.count('<dl class="facts-table">') == 2
    assert 'class="panel"' not in content


def test_account_sections_stay_consecutive_without_a_profile(client):
    member = create_user(username="account_no_profile")
    client.force_login(member)

    content = client.get(reverse("account")).content.decode()

    assert section_titles(content) == [
        ("01", "Account details"),
        ("02", "USYD and USU details"),
        ("03", "Security"),
    ]


def test_account_summary_shows_status_tag_name_path_and_researcher_tag(client):
    member = create_user(username="account_summary")
    MemberProfile.objects.create(
        user=member,
        display_name="Summary Member",
        is_published=True,
        researcher_number=7,
    )
    client.force_login(member)

    content = client.get(reverse("account")).content.decode()

    summary = content[content.index('<div class="account-summary">') :]
    summary = summary[: summary.index('<dl class="facts-table">')]
    assert '<p class="status-tag status-tag--open">Published</p>' in summary
    assert '<p class="gold-tag">Researcher 07</p>' in summary
    assert summary.index("Published") < summary.index("Researcher 07")
    assert '<p class="account-summary__name">Summary Member</p>' in summary
    assert (
        '<p class="account-summary__path">'
        f"{reverse('members:detail', kwargs={'username': 'account_summary'})}</p>"
    ) in summary
    # No avatar: a decorative initial stands in, and the name is not repeated
    # as an accessible image name.
    assert (
        'class="account-summary__avatar-fallback" aria-hidden="true">S</div>' in summary
    )


@pytest.mark.parametrize(
    ("is_published", "is_hidden_by_admin", "tag"),
    (
        (False, False, '<p class="status-tag">Not published</p>'),
        (True, True, '<p class="status-tag">Unavailable on public pages</p>'),
    ),
)
def test_account_summary_uses_a_plain_tag_unless_published(
    client, is_published, is_hidden_by_admin, tag
):
    member = create_user(username="account_plain_tag")
    MemberProfile.objects.create(
        user=member,
        is_published=is_published,
        is_hidden_by_admin=is_hidden_by_admin,
    )
    client.force_login(member)

    content = client.get(reverse("account")).content.decode()

    assert tag in content
    assert "gold-tag" not in content
    # Without a display name the summary falls back to the username.
    assert '<p class="account-summary__name">account_plain_tag</p>' in content
