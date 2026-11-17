from datetime import timedelta

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client, override_settings
from django.utils import timezone

from apps.events.models import Event
from apps.safety.models import RiskNoticeVersion
from apps.safety.services import activate_risk_notice
from tests.browser_runner import run_node_scenario
from tests.factories import create_user
from tests.test_event_registration_pages import RISK_NOTICE_TEXT


@override_settings(RISK_NOTICE_DRAFT_VISIBLE=True)
class EventRegistrationBrowserTests(StaticLiveServerTestCase):
    @staticmethod
    def create_member(username):
        user = create_user(username, email=f"{username}@example.test", verified=True)
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

        run_node_scenario(
            "event-registration.mjs",
            self.live_server_url,
            extra_env={
                "NULDL_SESSION_COOKIE_NAME": settings.SESSION_COOKIE_NAME,
                "NULDL_JS_SESSION": self.create_member("event-js-member"),
                "NULDL_NOJS_SESSION": self.create_member("event-nojs-member"),
            },
            timeout=120,
        )
