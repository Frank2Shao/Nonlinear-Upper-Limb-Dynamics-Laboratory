import re
from html.parser import HTMLParser

import pytest
from django.urls import reverse


class HeadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self._current_level = None
        self._current_text = []

    def handle_starttag(self, tag, attrs):
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._current_level = int(tag[1])
            self._current_text = []

    def handle_data(self, data):
        if self._current_level is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag):
        if self._current_level is not None and tag == f"h{self._current_level}":
            text = " ".join("".join(self._current_text).split())
            self.headings.append((self._current_level, text))
            self._current_level = None
            self._current_text = []


def response_content(client, url_name):
    response = client.get(reverse(url_name))
    assert response.status_code == 200
    return response, response.content.decode()


def test_about_page_uses_approved_content_metadata_and_heading_order(client):
    response, content = response_content(client, "about")

    assert "core/about.html" in [template.name for template in response.templates]
    assert "<title>About NULDL Armwrestling Club</title>" in content
    description = (
        "Learn about NULDL Armwrestling Club, our training activities and our "
        "approach to technique, safety and inclusive participation."
    )
    assert f'<meta name="description" content="{description}">' in content
    assert f'<meta property="og:description" content="{description}">' in content

    parser = HeadingParser()
    parser.feed(content)
    assert parser.headings == [
        (1, "About NULDL Armwrestling Club"),
        (2, "Our Purpose"),
        (2, "What We Do"),
        (3, "Beginner induction sessions"),
        (3, "Regular supervised practice pulls"),
        (3, "Technique and rules workshops"),
        (3, "Internal competitions"),
        (2, "Who Can Participate?"),
        (2, "How We Train"),
    ]
    for approved_text in (
        "student-led, community-focused armwrestling club",
        "make armwrestling more accessible as a strength-and-skill sport",
        "Regular supervised practice pulls",
        "Internal competitions",
        "Website access does not automatically provide voting rights",
        "constitutional requirements",
        "Good armwrestling depends on technique, control and respect",
    ):
        assert approved_text in content
    assert "Social armwrestling sessions" not in content
    assert "Collaborative activities that support the club’s purpose" not in content
    assert '<p class="label-mono">About the club</p>' in content
    assert content.count('class="feature-card"') == 4
    assert content.count('class="report-section"') == 4


def test_beginners_safety_page_uses_approved_content_metadata_and_headings(client):
    response, content = response_content(client, "beginners_safety")

    assert "core/beginners_safety.html" in [
        template.name for template in response.templates
    ]
    assert "<title>Beginners and Safety | NULDL Armwrestling Club</title>" in content
    description = (
        "Learn what to expect at your first NULDL Armwrestling Club session and "
        "review the essential safety principles for participation."
    )
    assert f'<meta name="description" content="{description}">' in content
    assert f'<meta property="og:description" content="{description}">' in content

    parser = HeadingParser()
    parser.feed(content)
    assert parser.headings == [
        (1, "Beginners Are Welcome"),
        (2, "What to Expect"),
        (2, "Armwrestling Involves Risk"),
        (2, "Before Participating"),
        (2, "During Training"),
        (2, "Shared Responsibility"),
    ]
    for approved_text in (
        "fundamental techniques before controlled practice begins",
        "Guided and supervised practice pulls",
        "bone injury or fracture",
        "do not take part until you have obtained appropriate advice",
        "Do not force a movement through pain or loss of control",
        "Stop immediately if you experience pain, numbness, dizziness",
        "Safe training depends on clear communication",
    ):
        assert approved_text in content


@pytest.mark.parametrize("url_name", ["home", "about", "beginners_safety"])
@pytest.mark.django_db
def test_public_navigation_links_only_available_public_pages(client, url_name):
    _, content = response_content(client, url_name)

    for available_name in ("home", "about", "beginners_safety", "members:list"):
        assert f'href="{reverse(available_name)}"' in content
    assert f'href="{reverse(url_name)}" aria-current="page"' in content
    for unavailable_path in ("/locations/",):
        assert f'href="{unavailable_path}"' not in content
    assert "Risk Notice" not in content


@pytest.mark.parametrize("url_name", ["about", "beginners_safety"])
def test_public_information_pages_exclude_unapproved_details(client, url_name):
    _, content = response_content(client, url_name)

    assert re.search(r"\bNULDL\b(?! Armwrestling Club)", content) is None
    assert re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", content) is None
    for forbidden_text in (
        "USYD",
        "USU ID",
        "Sydney University",
        "University of Sydney",
        "Sydney’s CBD",
        "Venue details",
    ):
        assert forbidden_text not in content


def test_anonymous_about_join_action_targets_signup(client):
    _, content = response_content(client, "about")

    assert f'data-public-primary href="{reverse("account_signup")}">Join</a>' in content


@pytest.mark.parametrize("url_name", ["about", "beginners_safety"])
def test_member_public_pages_hide_join_actions(client, verified_member, url_name):
    client.force_login(verified_member)

    _, content = response_content(client, url_name)

    assert "data-public-primary" not in content
    assert f'href="{reverse("account_signup")}"' not in content
    assert "Create an Account" not in content
    assert "Join the Club" not in content


def test_beginners_safety_has_plural_expectations_and_no_bottom_cta(client):
    _, content = response_content(client, "beginners_safety")

    assert "Introductions to the session and equipment" in content
    assert "Explanations of basic rules and positions" in content
    assert "An introduction to the session and equipment" not in content
    assert "An explanation of basic rules and positions" not in content
    assert "data-public-primary" not in content
    assert "public-page__action" not in content
