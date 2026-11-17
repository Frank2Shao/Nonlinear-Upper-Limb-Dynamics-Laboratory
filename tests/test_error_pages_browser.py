from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings

from tests.browser_runner import run_node_scenario


@override_settings(DEBUG=False, ROOT_URLCONF="tests.error_urls")
class ErrorPagesBrowserTests(StaticLiveServerTestCase):
    def test_error_pages_desktop_mobile_keyboard_and_no_javascript(self):
        run_node_scenario(
            "error-pages.mjs",
            self.live_server_url,
        )
