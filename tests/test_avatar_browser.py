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
class AvatarBrowserTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.media_directory = tempfile.TemporaryDirectory()
        cls.media_override = override_settings(MEDIA_ROOT=cls.media_directory.name)
        cls.media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.media_override.disable()
        cls.media_directory.cleanup()

    def test_avatar_edit_interface_and_upload_error(self):
        image = BytesIO()
        Image.new("RGB", (12, 8), color="gold").save(image, format="PNG")
        user = User.objects.create_user(
            username="avatar-browser",
            email="avatar-browser@example.com",
            password="correct horse battery staple",
        )
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            primary=True,
            verified=True,
        )
        MemberProfile.objects.create(
            user=user,
            avatar=SimpleUploadedFile(
                "browser.png",
                image.getvalue(),
                content_type="image/png",
            ),
        )
        self.client.force_login(user)

        environment = os.environ.copy()
        environment["NULDL_LIVE_SERVER_URL"] = self.live_server_url
        environment["NULDL_SESSION_COOKIE_NAME"] = settings.SESSION_COOKIE_NAME
        environment["NULDL_SESSION_COOKIE_VALUE"] = self.client.cookies[
            settings.SESSION_COOKIE_NAME
        ].value
        script = Path(__file__).parent / "browser" / "avatar-edit.mjs"

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
