from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings

from tests.browser_runner import run_node_scenario


@override_settings(RISK_NOTICE_DRAFT_VISIBLE=True)
class DraftRiskNoticeBrowserTests(StaticLiveServerTestCase):
    def test_draft_mobile_keyboard_and_no_javascript(self):
        run_node_scenario(
            "draft-risk-notice.mjs",
            self.live_server_url,
        )
