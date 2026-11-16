import re
from pathlib import Path
from xml.etree import ElementTree

import pytest
from django.test import override_settings
from django.urls import reverse

PUBLIC_METADATA = (
    (
        "home",
        "NULDL Armwrestling Club | Training and Community",
        "Learn armwrestling technique, practise under supervision and join a "
        "welcoming strength-sport community. Beginners are welcome.",
    ),
    (
        "about",
        "About NULDL Armwrestling Club",
        "Learn about NULDL Armwrestling Club, our training activities and our "
        "approach to technique, safety and inclusive participation.",
    ),
    (
        "beginners_safety",
        "Beginners and Safety | NULDL Armwrestling Club",
        "Learn what to expect at your first NULDL Armwrestling Club session and "
        "review the essential safety principles for participation.",
    ),
)


@pytest.mark.parametrize(("url_name", "title", "description"), PUBLIC_METADATA)
@pytest.mark.django_db
def test_public_pages_use_approved_metadata_and_open_graph(
    client, url_name, title, description
):
    path = reverse(url_name)
    response = client.get(path)

    assert response.status_code == 200
    content = response.content.decode()
    assert f"<title>{title}</title>" in content
    assert f'<meta name="description" content="{description}">' in content
    assert '<meta property="og:type" content="website">' in content
    assert '<meta property="og:site_name" content="NULDL Armwrestling Club">' in content
    assert f'<meta property="og:title" content="{title}">' in content
    assert f'<meta property="og:description" content="{description}">' in content
    assert f'<meta property="og:url" content="http://testserver{path}">' in content
    assert 'rel="canonical"' not in content
    assert "nuldl.com" not in content


def sitemap_locations(client):
    response = client.get(reverse("sitemap"))

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/xml")
    root = ElementTree.fromstring(response.content)
    namespace = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return response, [
        node.text for node in root.findall("sitemap:url/sitemap:loc", namespace)
    ]


def test_sitemap_contains_only_production_public_pages(client):
    response, locations = sitemap_locations(client)

    assert "core/sitemap.xml" in [template.name for template in response.templates]
    assert locations == [
        "http://testserver/",
        "http://testserver/about/",
        "http://testserver/beginners-safety/",
        "http://testserver/members/",
    ]
    sitemap_content = response.content.decode()
    for excluded_path in (
        "/accounts/",
        "/account/",
        "/admin/",
        "/risk-notice/",
        "/events/",
        "/members/example-member/",
        "/locations/",
        "/test-error/",
    ):
        assert excluded_path not in sitemap_content


@override_settings(RISK_NOTICE_DRAFT_VISIBLE=True)
def test_sitemap_never_includes_draft_risk_notice(client):
    _, locations = sitemap_locations(client)

    assert "http://testserver/risk-notice/" not in locations
    assert locations == [
        "http://testserver/",
        "http://testserver/about/",
        "http://testserver/beginners-safety/",
        "http://testserver/members/",
    ]


@pytest.mark.parametrize("url_name", ["home", "about", "beginners_safety"])
@pytest.mark.django_db
def test_footer_exposes_only_approved_instagram_contact(client, url_name):
    content = client.get(reverse(url_name)).content.decode()

    assert (
        'href="https://www.instagram.com/nuldl_armwrestlingclub/">Follow NULDL '
        "Armwrestling Club on Instagram: @nuldl_armwrestlingclub</a>"
    ) in content
    assert re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", content) is None
    assert "mailto:" not in content
    assert "Sydney University" not in content
    assert "University of Sydney" not in content


def test_step_26_sources_do_not_hardcode_a_canonical_host():
    project_root = Path(__file__).parents[1]
    source_paths = (
        project_root / "apps" / "core" / "views.py",
        project_root / "apps" / "core" / "urls.py",
        project_root / "apps" / "core" / "templates" / "core" / "base.html",
        project_root
        / "apps"
        / "core"
        / "templates"
        / "core"
        / "includes"
        / "footer.html",
        project_root / "apps" / "core" / "templates" / "core" / "sitemap.xml",
    )

    combined_source = "\n".join(
        path.read_text(encoding="utf-8") for path in source_paths
    )
    assert "nuldl.com" not in combined_source
    assert "testserver" not in combined_source
    assert 'rel="canonical"' not in combined_source
