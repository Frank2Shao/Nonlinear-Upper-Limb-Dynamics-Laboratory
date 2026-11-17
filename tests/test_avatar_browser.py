import tempfile
from io import BytesIO

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from apps.members.models import MemberProfile
from tests.browser_runner import run_node_scenario
from tests.factories import create_user


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
        user = create_user("avatar-browser", verified=True)
        MemberProfile.objects.create(
            user=user,
            avatar=SimpleUploadedFile(
                "browser.png",
                image.getvalue(),
                content_type="image/png",
            ),
        )
        self.client.force_login(user)

        run_node_scenario(
            "avatar-edit.mjs",
            self.live_server_url,
            extra_env={
                "NULDL_SESSION_COOKIE_NAME": settings.SESSION_COOKIE_NAME,
                "NULDL_SESSION_COOKIE_VALUE": self.client.cookies[
                    settings.SESSION_COOKIE_NAME
                ].value,
            },
        )
