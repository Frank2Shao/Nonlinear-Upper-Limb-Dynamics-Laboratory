import os
import subprocess
from datetime import timedelta
from pathlib import Path

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client, override_settings
from django.utils import timezone

from apps.accounts.models import User
from apps.events.models import Event
from apps.safety.models import RiskNoticeVersion
from apps.safety.services import activate_risk_notice
from tests.test_event_registration_pages import RISK_NOTICE_TEXT


@override_settings(RISK_NOTICE_DRAFT_VISIBLE=True)
class EventRegistrationBrowserTests(StaticLiveServerTestCase):
    @staticmethod
    def create_member(username):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.test",
            password="test-password",
        )
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=True,
            primary=True,
        )
        client = Client()
        client.force_login(user)
        return client.cookies[settings.SESSION_COOKIE_NAME].value

    def test_modal_and_no_javascript_registration(self):
        start = timezone.now() + timedelta(days=3)
        Event.objects.create(
            title="Synthetic Registration Session",
            slug="synthetic-registration",
            description="Synthetic event description.",
            starts_at=start,
            ends_at=start + timedelta(hours=1),
            is_published=True,
            registration_open=True,
        )
        notice = RiskNoticeVersion.objects.create(
            version="synthetic-en-v1",
            body=RISK_NOTICE_TEXT,
        )
        activate_risk_notice(notice.pk)

        environment = os.environ.copy()
        environment["NULDL_LIVE_SERVER_URL"] = self.live_server_url
        environment["NULDL_SESSION_COOKIE_NAME"] = settings.SESSION_COOKIE_NAME
        environment["NULDL_JS_SESSION"] = self.create_member("event-js-member")
        environment["NULDL_NOJS_SESSION"] = self.create_member("event-nojs-member")
        script = Path(__file__).parent / "browser" / "event-registration.mjs"
        result = subprocess.run(
            ["node", str(script)],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=120,
        )

        assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")
