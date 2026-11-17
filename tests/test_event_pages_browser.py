from datetime import timedelta

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone

from apps.events.models import Event
from tests.browser_runner import run_node_scenario


class EventPagesBrowserTests(StaticLiveServerTestCase):
    def test_events_on_desktop_mobile_and_without_javascript(self):
        start = timezone.now() + timedelta(days=3)
        Event.objects.create(
            title="Synthetic Training Session",
            slug="synthetic-training",
            description="Synthetic event description.",
            starts_at=start,
            ends_at=start + timedelta(hours=1),
            is_published=True,
            map_url="https://maps.google.com/?q=synthetic",
        )
        run_node_scenario(
            "event-pages.mjs",
            self.live_server_url,
        )
