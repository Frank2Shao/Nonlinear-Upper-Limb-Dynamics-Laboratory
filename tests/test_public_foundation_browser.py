from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from tests.browser_runner import run_node_scenario


class PublicFoundationBrowserTests(StaticLiveServerTestCase):
    def test_desktop_mobile_keyboard_and_no_javascript_navigation(self):
        run_node_scenario(
            "public-foundation.mjs",
            self.live_server_url,
        )
