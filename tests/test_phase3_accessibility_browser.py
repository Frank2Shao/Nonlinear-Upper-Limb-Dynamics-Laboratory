import os
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from apps.accounts.models import User
from apps.members.models import MemberProfile


@override_settings(
    ROOT_URLCONF="tests.profile_media_urls",
    MEDIA_URL="/test-media/",
)
class PhaseThreeAccessibilityBrowserTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.media_directory = tempfile.TemporaryDirectory()
        cls.media_path = Path(cls.media_directory.name)
        cls.media_override = override_settings(MEDIA_ROOT=cls.media_directory.name)
        cls.media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.media_override.disable()
        cls.media_directory.cleanup()
        assert not cls.media_path.exists()

    @staticmethod
    def create_avatar(filename: str) -> SimpleUploadedFile:
        image = BytesIO()
        Image.new("RGB", (18, 12), color="gold").save(image, format="PNG")
        return SimpleUploadedFile(filename, image.getvalue(), content_type="image/png")

    @staticmethod
    def create_verified_user(username: str) -> User:
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
        return user

    def run_scenario(self, **extra_environment: str) -> None:
        environment = os.environ.copy()
        environment["NULDL_LIVE_SERVER_URL"] = self.live_server_url
        environment.update(extra_environment)
        script = Path(__file__).parent / "browser" / "phase3-accessibility.mjs"

        result = subprocess.run(
            ["node", str(script)],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=240,
        )

        output = (result.stdout or "") + (result.stderr or "")
        assert result.returncode == 0, output

    def test_phase_three_profile_pages_meet_accessibility_and_browser_checks(self):
        owner_username = "phase3_" + "member" * 18
        owner = self.create_verified_user(owner_username)
        MemberProfile.objects.create(
            user=owner,
            avatar=self.create_avatar("owner.png"),
            bio="UnbrokenOwnerBiography" + "a" * 300,
            is_published=True,
            is_hidden_by_admin=True,
        )

        public_username = "public_" + "profile" * 17
        public_user = self.create_verified_user(public_username)
        MemberProfile.objects.create(
            user=public_user,
            display_name="A public member with a deliberately long display name for responsive checks",
            avatar=self.create_avatar("public.png"),
            bio="Long public biography UnbrokenPublicBiography" + "b" * 300,
            experience_level=MemberProfile.ExperienceLevel.ONE_TO_THREE_YEARS,
            preferred_arm=MemberProfile.PreferredArm.BOTH,
            instagram_handle="phase3.public_member",
            other_social_url="https://example.com/phase3-public-member",
            is_published=True,
        )
        self.client.force_login(owner)

        self.run_scenario(
            NULDL_SESSION_COOKIE_NAME=settings.SESSION_COOKIE_NAME,
            NULDL_SESSION_COOKIE_VALUE=self.client.cookies[
                settings.SESSION_COOKIE_NAME
            ].value,
            NULDL_PHASE3_DETAIL_PATH=f"/members/{public_username}/",
            NULDL_PHASE3_OWNER_USERNAME=owner_username,
        )

    def test_phase_three_members_empty_state_remains_responsive_without_javascript(
        self,
    ):
        self.run_scenario(NULDL_PHASE3_MODE="empty")
