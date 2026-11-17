from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings

from tests.browser_runner import run_node_scenario


@override_settings(
    DEBUG=False,
    ROOT_URLCONF="tests.error_urls",
    RISK_NOTICE_DRAFT_VISIBLE=True,
)
class PhaseTwoAccessibilityBrowserTests(StaticLiveServerTestCase):
    def test_public_pages_meet_phase_two_accessibility_risk_checks(self):
        run_node_scenario(
            "phase2-accessibility.mjs",
            self.live_server_url,
            timeout=180,
        )
