import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.fixture
def verified_member(db):
    user = get_user_model().objects.create_user(
        username="member@example.com",
        email="member@example.com",
        password="test-password",
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        primary=True,
        verified=True,
    )
    return user


def test_home_uses_accessible_global_page_shell(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert '<html lang="en">' in content
    assert (
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        in content
    )
    assert 'href="#main-content">Skip to main content</a>' in content
    assert '<header class="site-header">' in content
    assert 'aria-label="Primary navigation"' in content
    assert 'id="main-content" tabindex="-1"' in content
    assert '<footer class="site-footer">' in content
    assert content.count("<h1") == 1
    assert 'href="/" aria-current="page"' in content


def test_anonymous_header_shows_authentication_links(client):
    response = client.get(reverse("home"))

    content = response.content.decode()
    assert f'href="{reverse("account_login")}"' in content
    assert f'href="{reverse("account_signup")}"' in content
    assert "Log in" in content
    assert "Join the Club" in content
    assert f'href="{reverse("account")}"' not in content


def test_member_header_shows_account_link(client, verified_member):
    client.force_login(verified_member)

    response = client.get(reverse("home"))

    content = response.content.decode()
    assert f'href="{reverse("account")}"' in content
    assert "Log in" not in content
    assert "Join the Club" not in content


def test_account_page_uses_shared_shell_and_marks_current_navigation(
    client, verified_member
):
    client.force_login(verified_member)

    response = client.get(reverse("account"))

    assert response.status_code == 200
    content = response.content.decode()
    assert '<header class="site-header">' in content
    assert 'id="main-content" tabindex="-1"' in content
    assert '<footer class="site-footer">' in content
    assert content.count("<h1") == 1
    assert f'href="{reverse("account")}" aria-current="page"' in content


def test_framework_messages_are_announced(client, verified_member):
    client.force_login(verified_member)

    response = client.post(
        reverse("account"),
        {"is_usyd_student": "on", "usu_id": "00112233"},
        follow=True,
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert 'aria-live="polite"' in content
    assert 'aria-atomic="true"' in content
    assert 'role="status"' in content
    assert "Your account information has been updated." in content


def test_primary_navigation_works_without_javascript(client):
    response = client.get(reverse("home"))

    content = response.content.decode()
    assert "onclick=" not in content
    assert 'defer src="/static/vendor/alpine/alpine.min.js"' in content
    assert f'href="{reverse("home")}"' in content
    assert f'href="{reverse("account_login")}"' in content
    assert f'href="{reverse("account_signup")}"' in content
