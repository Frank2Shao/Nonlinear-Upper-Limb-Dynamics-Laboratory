import os
import subprocess
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class HomeBrowserTests(StaticLiveServerTestCase):
    def test_home_desktop_mobile_and_no_javascript(self):
        environment = os.environ.copy()
        environment["NULDL_LIVE_SERVER_URL"] = self.live_server_url
        script = Path(__file__).parent / "browser" / "home-page.mjs"

        result = subprocess.run(
            ["node", str(script)],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=90,
        )

        output = (result.stdout or "") + (result.stderr or "")
        assert result.returncode == 0, output
