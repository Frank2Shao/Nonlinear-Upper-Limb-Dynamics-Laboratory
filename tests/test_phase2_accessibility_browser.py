import os
import subprocess
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings


@override_settings(
    DEBUG=False,
    ROOT_URLCONF="tests.error_urls",
    RISK_NOTICE_DRAFT_VISIBLE=True,
)
class PhaseTwoAccessibilityBrowserTests(StaticLiveServerTestCase):
    def test_public_pages_meet_phase_two_accessibility_risk_checks(self):
        environment = os.environ.copy()
        environment["NULDL_LIVE_SERVER_URL"] = self.live_server_url
        script = Path(__file__).parent / "browser" / "phase2-accessibility.mjs"

        result = subprocess.run(
            ["node", str(script)],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=180,
        )

        output = (result.stdout or "") + (result.stderr or "")
        assert result.returncode == 0, output
