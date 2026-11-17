from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from tests.browser_runner import run_node_scenario


class AuthenticationBrowserSmokeTests(StaticLiveServerTestCase):
    def test_mobile_keyboard_alpine_paste_focus_and_no_javascript(self):
        run_node_scenario(
            "authentication-ui.mjs",
            self.live_server_url,
        )
