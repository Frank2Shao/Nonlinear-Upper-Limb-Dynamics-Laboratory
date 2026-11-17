from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from tests.browser_runner import run_node_scenario


class HomeBrowserTests(StaticLiveServerTestCase):
    def test_home_desktop_mobile_and_no_javascript(self):
        run_node_scenario(
            "home-page.mjs",
            self.live_server_url,
        )
