import os
import subprocess
from pathlib import Path

from allauth.account.models import EmailAddress
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from apps.accounts.models import User
from apps.members.models import MemberProfile


class MemberDirectoryBrowserTests(StaticLiveServerTestCase):
    def test_directory_desktop_mobile_keyboard_and_no_javascript(self):
        for username, display_name in (
            ("browser-alpha", "Alpha Member"),
            ("browser-bravo", "Bravo Member"),
        ):
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="test-password",
            )
            EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=True,
            )
            MemberProfile.objects.create(
                user=user,
                display_name=display_name,
                is_published=True,
                experience_level=MemberProfile.ExperienceLevel.UNDER_ONE_YEAR,
                preferred_arm=MemberProfile.PreferredArm.RIGHT,
                bio=f"Public bio for {display_name}.",
                instagram_handle=f"{username.replace('-', '_')}.club",
                other_social_url=f"https://example.com/{username}",
            )

        environment = os.environ.copy()
        environment["NULDL_LIVE_SERVER_URL"] = self.live_server_url
        script = Path(__file__).parent / "browser" / "member-directory.mjs"

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
