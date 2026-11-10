import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.fixture
def verified_member(db):
    user = get_user_model().objects.create_user(
        username="home-member",
        email="home-member@example.com",
        password="test-password",
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        primary=True,
        verified=True,
    )
    return user


def test_home_uses_approved_metadata_and_content(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "<title>NULDL Armwrestling Club | Training and Community</title>" in content
    description = (
        "Learn armwrestling technique, practise under supervision and join a "
        "welcoming strength-sport community. Beginners are welcome."
    )
    assert f'<meta name="description" content="{description}">' in content
    assert f'<meta property="og:description" content="{description}">' in content
    assert "Studying chaotic upper-limb interactions since 2026." in content
    assert "Nonlinear Upper Limb Dynamics Laboratory" in content
    assert "NULDL Armwrestling Club is an armwrestling community" in content
    assert "New to Armwrestling?" in content
    assert "Join Us !" in content
    assert "Beginner Induction" in content
    assert "Supervised Practice" in content
    assert "Technique and Rules" in content
    assert "Community and Competition" in content
    assert "No previous experience is required" not in content
    assert "You will have time to ask questions" not in content
    assert "Open to New Participants" not in content


def test_home_exposes_only_the_approved_static_session(client):
    response = client.get(reverse("home"))

    content = response.content.decode()
    assert "Upcoming Session" in content
    assert "1 December 2026" in content
    assert "3:00–7:00 pm" in content
    assert "Training Session" in content
    assert "Venue details to be confirmed" in content
    assert "Further attendance details will be published before the session." in content
    assert 'href="/events/"' not in content
    assert "Register for this event" not in content
    assert "registration status" not in content.lower()


def test_anonymous_home_ctas_point_to_signup_and_beginner_content(client):
    response = client.get(reverse("home"))

    content = response.content.decode()
    assert content.count(f'href="{reverse("account_signup")}"') >= 3
    assert 'data-home-primary href="/accounts/signup/">Join the Club</a>' in content
    assert 'data-session-join href="/accounts/signup/">Join</a>' in content
    assert 'href="#new-to-armwrestling">New to Armwrestling?</a>' in content


def test_member_home_hides_redundant_join_actions(client, verified_member):
    client.force_login(verified_member)

    response = client.get(reverse("home"))

    content = response.content.decode()
    assert "data-home-primary" not in content
    assert "data-session-join" not in content
    assert f'href="{reverse("account_signup")}"' not in content
    assert "Join the Club" not in content
    assert 'href="#new-to-armwrestling">New to Armwrestling?</a>' in content


def test_home_uses_responsive_logo_without_restricted_branding(client):
    response = client.get(reverse("home"))

    content = response.content.decode()
    for width in (480, 800, 1200):
        assert f"/static/images/brand/nuldl-club-logo-{width}.webp" in content
    assert 'width="800"' in content
    assert 'height="800"' in content
    assert 'alt="Nonlinear Upper Limb Dynamics Laboratory logo"' in content
    for restricted_term in (
        "USYD",
        "Sydney University",
        "University of Sydney",
    ):
        assert restricted_term not in content
