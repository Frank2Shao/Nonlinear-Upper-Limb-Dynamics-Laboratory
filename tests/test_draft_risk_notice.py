import os
import re
import subprocess
import sys

import pytest
from django.test import override_settings
from django.urls import reverse

DRAFT_PARAGRAPHS = (
    "This public arm wrestling experience is a voluntary, high-intensity "
    "competitive activity. Arm wrestling involves inherent risks of injury, "
    "including but not limited to muscle strain, tendon or ligament injury, "
    "joint sprain or dislocation, bone injury and fracture. Some risks may not "
    "be fully foreseeable or avoidable.",
    "Before participating, please confirm that you do not have a condition that "
    "makes competitive physical activity unsuitable for you, including previous "
    "shoulder, elbow or wrist injuries or other musculoskeletal conditions, "
    "cardiovascular or cerebrovascular disease, osteoporosis, neurological "
    "conditions, or similar health concerns. If you are unsure about your fitness "
    "to participate, do not take part. Stop immediately if you experience pain, "
    "numbness, dizziness or other discomfort.",
    "By participating, you acknowledge and voluntarily accept the potential risks "
    "described above and confirm that you are choosing to participate based on "
    "your own physical condition. To the maximum extent permitted by law, the "
    "activity organiser, venue provider and relevant staff accept no liability "
    "for injury or loss arising from the inherent or obvious risks of the "
    "activity. Nothing in this notice excludes or limits any liability that "
    "cannot lawfully be excluded or limited. By participating, you acknowledge "
    "that you have read and understood this risk notice and voluntarily choose "
    "to take part.",
    "By participating, you acknowledge that you have read and understood this "
    "risk notice. If you are unsure about your health or the risks of the "
    "activity, do not participate.",
)


def run_settings_import(module_name: str, draft_value: str | None):
    environment = os.environ.copy()
    if draft_value is None:
        environment.pop("RISK_NOTICE_DRAFT_VISIBLE", None)
    else:
        environment["RISK_NOTICE_DRAFT_VISIBLE"] = draft_value

    return subprocess.run(
        [
            sys.executable,
            "-c",
            (
                f"import {module_name} as settings; "
                "print(settings.RISK_NOTICE_DRAFT_VISIBLE)"
            ),
        ],
        capture_output=True,
        check=False,
        env=environment,
        text=True,
    )


def test_environment_settings_keep_draft_visibility_explicit_and_safe():
    development = run_settings_import("config.settings.development", None)
    preview = run_settings_import("config.settings.preview", "true")
    production = run_settings_import("config.settings.production", "true")
    preview_without_approval = run_settings_import("config.settings.preview", None)

    assert development.returncode == 0
    assert development.stdout.strip() == "True"
    assert preview.returncode == 0
    assert preview.stdout.strip() == "True"
    assert production.returncode == 0
    assert production.stdout.strip() == "False"
    assert preview_without_approval.returncode != 0
    assert "RISK_NOTICE_DRAFT_VISIBLE" in preview_without_approval.stderr


def test_draft_is_closed_by_default_and_not_discoverable(client):
    risk_notice_path = reverse("safety:risk_notice")

    assert client.get(risk_notice_path).status_code == 404
    for url_name in ("home", "about", "beginners_safety"):
        content = client.get(reverse(url_name)).content.decode()
        assert risk_notice_path not in content
        assert "Draft Risk Notice" not in content
        assert "Read the Draft Risk Notice" not in content


@override_settings(RISK_NOTICE_DRAFT_VISIBLE=True)
@pytest.mark.django_db
def test_enabled_draft_uses_exact_approved_copy_and_noindex(
    client, django_assert_num_queries
):
    with django_assert_num_queries(0):
        response = client.get(reverse("safety:risk_notice"))

    assert response.status_code == 200
    assert "safety/risk_notice.html" in [
        template.name for template in response.templates
    ]
    content = response.content.decode()
    assert "<title>Draft Risk Notice | NULDL Armwrestling Club</title>" in content
    assert '<meta name="robots" content="noindex, nofollow">' in content
    assert "DRAFT — NOT APPROVED FOR PARTICIPATION USE" in content
    assert (
        "This draft is displayed for development and review purposes only. It has "
        "not been approved as the final NULDL Armwrestling Club Risk Notice and "
        "must not be relied upon as the terms for participation."
    ) in content
    for paragraph in DRAFT_PARAGRAPHS:
        assert paragraph in content
    assert (
        content.count(
            "By participating, you acknowledge that you have read and understood this "
            "risk notice"
        )
        == 2
    )


@override_settings(RISK_NOTICE_DRAFT_VISIBLE=True)
def test_enabled_draft_has_navigation_and_risk_panel_action(client):
    path = reverse("safety:risk_notice")
    draft_content = client.get(path).content.decode()
    beginners_content = client.get(reverse("beginners_safety")).content.decode()

    assert f'href="{path}" aria-current="page">Draft Risk Notice</a>' in draft_content
    assert (
        f'data-draft-risk-notice href="{path}">Read the Draft Risk Notice</a>'
        in beginners_content
    )
    assert re.search(
        r'<section class="public-section safety-panel".*?data-draft-risk-notice.*?'
        r"</section>",
        beginners_content,
        re.DOTALL,
    )
    assert "data-public-primary" not in beginners_content
    assert "public-page__action" not in beginners_content
    assert f'href="{path}">Draft Risk Notice</a>' in beginners_content


@override_settings(RISK_NOTICE_DRAFT_VISIBLE=True)
@pytest.mark.parametrize("url_name", ["home", "about", "beginners_safety"])
def test_enabled_draft_is_linked_from_public_header(client, url_name):
    content = client.get(reverse(url_name)).content.decode()

    assert f'href="{reverse("safety:risk_notice")}"' in content


@override_settings(RISK_NOTICE_DRAFT_VISIBLE=True)
def test_draft_has_no_confirmation_registration_or_data_form(client):
    content = client.get(reverse("safety:risk_notice")).content.decode()
    content_lower = content.lower()

    for forbidden_markup in (
        "<form",
        "<input",
        'type="checkbox"',
        'method="post"',
        "csrfmiddlewaretoken",
    ):
        assert forbidden_markup not in content_lower
    for forbidden_feature in (
        "Register for",
        "Submit acknowledgement",
        "Confirm participation",
        "RiskNoticeVersion",
    ):
        assert forbidden_feature not in content
