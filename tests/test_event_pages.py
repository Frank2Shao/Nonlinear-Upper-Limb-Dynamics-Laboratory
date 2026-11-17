import re
from datetime import UTC, datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from apps.events.models import Event
from apps.safety.models import RiskNoticeVersion

pytestmark = pytest.mark.django_db
SYDNEY = ZoneInfo("Australia/Sydney")


def event(slug, start, *, public=True, **overrides):
    values = {
        "title": slug,
        "slug": slug,
        "description": "Synthetic event description.",
        "starts_at": start,
        "ends_at": start + timedelta(hours=1),
        "is_published": public,
    }
    values.update(overrides)
    return Event.objects.create(**values)


def test_listing_filters_after_sydney_midnight_independent_of_active_timezone(client):
    first = event("earlier", datetime(2026, 12, 1, 17, tzinfo=SYDNEY))
    event("private", datetime(2026, 12, 4, 17, tzinfo=SYDNEY), public=False)
    event("later", datetime(2026, 12, 3, 17, tzinfo=SYDNEY))
    with (
        timezone.override(UTC),
        patch(
            "django.utils.timezone.now",
            return_value=datetime(2026, 12, 1, 23, 59, tzinfo=SYDNEY),
        ),
    ):
        response = client.get(reverse("events:list"))
        assert list(response.context["events"]) == [
            first,
            Event.objects.get(slug="later"),
        ]
        assert "private" not in response.content.decode()
    with (
        timezone.override(UTC),
        patch(
            "django.utils.timezone.now",
            return_value=datetime(2026, 12, 2, 0, 0, tzinfo=SYDNEY),
        ),
    ):
        upcoming = client.get(reverse("events:list"), {"view": "upcoming"})
        past = client.get(reverse("events:list"), {"view": "past"})
        invalid_filter = client.get(reverse("events:list"), {"view": "all"})
        assert [item.slug for item in upcoming.context["events"]] == ["later"]
        assert [item.slug for item in past.context["events"]] == ["earlier"]
        assert invalid_filter.context["selected"] == "upcoming"
        assert [item.slug for item in invalid_filter.context["events"]] == ["later"]
        assert ">All</a>" not in invalid_filter.content.decode()
        assert "Past event" in past.content.decode()


def test_home_shows_only_three_public_upcoming_events_and_links(client):
    now = timezone.now()
    for index in range(4):
        event(f"upcoming-{index}", now + timedelta(days=index + 1))
    event("private", now + timedelta(days=1), public=False)
    event("past", now - timedelta(days=5))
    content = client.get(reverse("home")).content.decode()
    assert all(f"upcoming-{index}" in content for index in range(3))
    assert "upcoming-3" not in content
    assert "private" not in content
    assert 'href="/events/"' in content
    assert reverse("events:detail", args=["upcoming-0"]) in content


@override_settings(RISK_NOTICE_DRAFT_VISIBLE=True)
def test_event_cards_show_bold_registration_status(client):
    now = timezone.now()
    event("open-event", now + timedelta(days=1), registration_open=True)
    event("closed-event", now + timedelta(days=2), registration_open=False)

    without_notice = client.get(reverse("events:list")).content.decode()
    assert '<p class="event-status">Registration open</p>' not in without_notice
    assert (
        without_notice.count('<p class="event-status">Registration unavailable</p>')
        == 2
    )

    RiskNoticeVersion.objects.create(
        version="synthetic-crlf",
        body="SYNTHETIC TEST ONLY\r\nCurrent notice.",
        is_current=True,
    )
    list_content = client.get(reverse("events:list")).content.decode()
    home_content = client.get(reverse("home")).content.decode()

    for content in (list_content, home_content):
        assert '<p class="event-status">Registration open</p>' in content
        assert '<p class="event-status">Registration unavailable</p>' in content


def test_events_navigation_marks_list_and_detail_current(client):
    public = event("navigation-event", timezone.now() + timedelta(days=1))

    for url in (
        reverse("events:list"),
        reverse("events:detail", args=[public.slug]),
    ):
        content = client.get(url).content.decode()
        assert (
            f'href="{reverse("events:list")}" aria-current="page">Events</a>' in content
        )


def test_detail_enforces_visibility_escaping_and_map_link(client):
    now = timezone.now()
    public = event(
        "public-event",
        now + timedelta(days=1),
        title="<script>unsafe</script>",
        map_url="https://maps.google.com/?q=synthetic",
    )
    event("hidden-event", now + timedelta(days=1), public=False)
    response = client.get(reverse("events:detail", args=[public.slug]))
    content = response.content.decode()
    assert response.status_code == 200
    assert "&lt;script&gt;unsafe&lt;/script&gt;" in content
    assert 'href="https://maps.google.com/?q=synthetic"' in content
    assert 'rel="noopener noreferrer"' in content
    assert "View location in map" in content
    assert "<form" not in content
    assert (
        client.get(reverse("events:detail", args=["hidden-event"])).status_code == 404
    )
    assert client.get(reverse("events:detail", args=["missing"])).status_code == 404


def test_event_views_provide_empty_states_and_without_map(client):
    assert "No events found." in client.get(reverse("events:list")).content.decode()
    public = event("no-map", timezone.now() + timedelta(days=1))
    response = client.get(reverse("events:detail", args=[public.slug]))
    assert "View location in map" not in response.content.decode()
    assert re.search(
        r'<p class="event-status" role="status"[^>]*>Registration unavailable</p>',
        response.content.decode(),
    )
    assert client.post(reverse("events:detail", args=[public.slug])).status_code == 405
