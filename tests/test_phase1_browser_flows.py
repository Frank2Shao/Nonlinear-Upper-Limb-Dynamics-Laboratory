import json
import os
import subprocess
import tempfile
from importlib import import_module
from pathlib import Path

from allauth.account.internal.flows.email_verification_by_code import (
    EMAIL_VERIFICATION_CODE_SESSION_KEY,
)
from allauth.account.internal.stagekit import LOGIN_SESSION_KEY
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from apps.accounts.services import update_usu_identity

User = get_user_model()
PASSWORD = "A-valid-password-2026"
SCRIPT = Path(__file__).parent / "browser" / "phase1-core-flows.mjs"


class Phase1CoreBrowserFlowTests(StaticLiveServerTestCase):
    def run_scenario(self, scenario: str, **values: object) -> None:
        environment = os.environ.copy()
        environment.update(
            {
                "NULDL_BROWSER_SCENARIO": scenario,
                "NULDL_LIVE_SERVER_URL": self.live_server_url,
                **{key: str(value) for key, value in values.items()},
            }
        )
        result = subprocess.run(
            ["node", str(SCRIPT)],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=90,
        )
        output = (result.stdout or "") + (result.stderr or "")
        assert result.returncode == 0, output

    def session_data(self, storage_state: str) -> dict[str, object]:
        state = json.loads(Path(storage_state).read_text(encoding="utf-8"))
        session_cookie = next(
            cookie
            for cookie in state["cookies"]
            if cookie["name"] == settings.SESSION_COOKIE_NAME
        )
        session_store = import_module(settings.SESSION_ENGINE).SessionStore(
            session_key=session_cookie["value"]
        )
        return dict(session_store.load())

    def create_verified_user(self, *, username: str, email: str):
        user = User.objects.create_user(
            username=username,
            email=email,
            password=PASSWORD,
        )
        EmailAddress.objects.create(
            user=user,
            email=email,
            primary=True,
            verified=True,
        )
        return user

    def test_signup_verification_account_and_logout_flow(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            storage_state = str(Path(temporary_directory) / "signup-state.json")
            self.run_scenario(
                "signup",
                NULDL_STORAGE_STATE=storage_state,
                NULDL_USERNAME="browser_signup",
                NULDL_EMAIL="browser-signup@example.net",
                NULDL_PASSWORD=PASSWORD,
                NULDL_USU_ID="12345678",
            )
            session = self.session_data(storage_state)
            code = session[EMAIL_VERIFICATION_CODE_SESSION_KEY]["code"]

            self.run_scenario(
                "verify-signup",
                NULDL_STORAGE_STATE=storage_state,
                NULDL_USERNAME="browser_signup",
                NULDL_CODE=code,
            )

        user = User.objects.get(username="browser_signup")
        assert user.is_usyd_student is True
        assert user.usu_id == "12345678"
        assert user.usu_review_status == User.UsuReviewStatus.PENDING
        assert EmailAddress.objects.get(user=user).verified is True
        assert user.member_profile.is_published is False

    def test_password_login_account_update_and_logout_flow(self):
        user = self.create_verified_user(
            username="browser_password",
            email="browser-password@example.net",
        )

        self.run_scenario(
            "password-login",
            NULDL_USERNAME=user.username,
            NULDL_PASSWORD=PASSWORD,
            NULDL_USU_ID="23456789",
        )

        user.refresh_from_db()
        assert user.is_usyd_student is True
        assert user.usu_id == "23456789"
        assert user.usu_review_status == User.UsuReviewStatus.PENDING

    def test_magic_code_login_and_logout_flow(self):
        user = self.create_verified_user(
            username="browser_magic",
            email="browser-magic@example.net",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            storage_state = str(Path(temporary_directory) / "magic-state.json")
            self.run_scenario(
                "magic-request",
                NULDL_STORAGE_STATE=storage_state,
                NULDL_EMAIL=user.email,
            )
            session = self.session_data(storage_state)
            code = session[LOGIN_SESSION_KEY]["state"]["stages"]["login_by_code"][
                "data"
            ]["code"]

            self.run_scenario(
                "magic-confirm",
                NULDL_STORAGE_STATE=storage_state,
                NULDL_CODE=code,
            )

    def test_admin_usu_review_flow(self):
        reviewer = self.create_verified_user(
            username="browser_reviewer",
            email="browser-reviewer@example.net",
        )
        reviewer.is_staff = True
        reviewer.save(update_fields=("is_staff",))
        reviewer.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="accounts",
                codename="review_usu_id",
            )
        )
        target = self.create_verified_user(
            username="browser_review_target",
            email="browser-review-target@example.net",
        )
        update_usu_identity(
            user=target,
            is_usyd_student=True,
            usu_id="34567890",
        )

        self.run_scenario(
            "admin-review",
            NULDL_USERNAME=reviewer.username,
            NULDL_PASSWORD=PASSWORD,
            NULDL_TARGET_USER_ID=target.pk,
        )

        target.refresh_from_db()
        assert target.usu_review_status == User.UsuReviewStatus.VERIFIED
        assert target.usu_reviewed_by == reviewer
