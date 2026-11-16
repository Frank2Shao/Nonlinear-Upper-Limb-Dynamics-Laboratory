import os
import subprocess
from datetime import timedelta
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone

from apps.events.models import Event


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
        environment = os.environ.copy()
        environment["NULDL_LIVE_SERVER_URL"] = self.live_server_url
        script = Path(__file__).parent / "browser" / "event-pages.mjs"
        result = subprocess.run(
            ["node", str(script)],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=90,
        )
        assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")
