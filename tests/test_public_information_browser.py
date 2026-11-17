from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from tests.browser_runner import run_node_scenario


class PublicInformationBrowserTests(StaticLiveServerTestCase):
    def test_public_pages_mobile_keyboard_zoom_and_no_javascript(self):
        run_node_scenario(
            "public-information.mjs",
            self.live_server_url,
        )
