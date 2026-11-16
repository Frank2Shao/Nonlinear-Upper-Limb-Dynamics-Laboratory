import pytest
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.urls import reverse

from apps.safety.models import RiskNoticeVersion
from apps.safety.services import activate_risk_notice

pytestmark = pytest.mark.django_db


@pytest.fixture
def versions():
    return tuple(
        RiskNoticeVersion.objects.create(
            version=label, body=f"SYNTHETIC TEST ONLY\nSample content {label}."
        )
        for label in ("test-1", "test-2")
    )


def test_switch_preserves_original_version(settings, versions):
    settings.RISK_NOTICE_DRAFT_VISIBLE = True
    old, new = versions
    activate_risk_notice(old.pk)
    old.refresh_from_db()
    previous_activation = old.activated_at
    activate_risk_notice(new.pk)
    old.refresh_from_db()
    new.refresh_from_db()
    assert not old.is_current
    assert old.activated_at == previous_activation
    assert old.body == "SYNTHETIC TEST ONLY\nSample content test-1."
    assert new.is_current
    assert new.activated_at is not None
    activate_risk_notice(new.pk)
    assert RiskNoticeVersion.objects.get(pk=new.pk).activated_at == new.activated_at


def test_database_rejects_two_current_versions(versions):
    old, new = versions
    RiskNoticeVersion.objects.filter(pk=old.pk).update(is_current=True)
    with pytest.raises(IntegrityError), transaction.atomic():
        RiskNoticeVersion.objects.filter(pk=new.pk).update(is_current=True)


def test_disabled_environment_blocks_admin_and_activation(admin_client, versions):
    url = reverse("admin:safety_risknoticeversion_changelist")
    assert admin_client.get(url).status_code == 403
    with pytest.raises(PermissionDenied):
        activate_risk_notice(versions[0].pk)
    assert not RiskNoticeVersion.objects.filter(is_current=True).exists()


def test_admin_can_activate_one_version(settings, admin_client, versions):
    settings.RISK_NOTICE_DRAFT_VISIBLE = True
    url = reverse("admin:safety_risknoticeversion_changelist")
    old, new = versions
    action = {"action": "make_current", "index": 0}
    admin_client.post(url, {**action, "_selected_action": [old.pk, new.pk]})
    assert not RiskNoticeVersion.objects.filter(is_current=True).exists()
    assert (
        admin_client.post(url, {**action, "_selected_action": [new.pk]}).status_code
        == 302
    )
    assert RiskNoticeVersion.objects.get(is_current=True) == new


def test_view_only_staff_cannot_activate(settings, client, django_user_model, versions):
    settings.RISK_NOTICE_DRAFT_VISIBLE = True
    staff = django_user_model.objects.create_user(
        username="safety-viewer", email="safety-viewer@example.test", is_staff=True
    )
    staff.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="safety", codename="view_risknoticeversion"
        )
    )
    client.force_login(staff)
    url = reverse("admin:safety_risknoticeversion_changelist")
    assert client.get(url).status_code == 200
    client.post(
        url,
        {"action": "make_current", "_selected_action": [versions[0].pk], "index": 0},
    )
    assert not RiskNoticeVersion.objects.filter(is_current=True).exists()


def test_admin_requires_synthetic_marker_and_keeps_version_readonly(
    settings, admin_client, versions
):
    settings.RISK_NOTICE_DRAFT_VISIBLE = True
    add_url = reverse("admin:safety_risknoticeversion_add")
    response = admin_client.post(
        add_url, {"version": "unmarked", "body": "Unmarked sample"}
    )
    assert b"Start the body with SYNTHETIC TEST ONLY" in response.content
    assert not RiskNoticeVersion.objects.filter(version="unmarked").exists()
    assert (
        admin_client.post(
            add_url, {"version": "marked", "body": "SYNTHETIC TEST ONLY\nSample"}
        ).status_code
        == 302
    )
    old = versions[0]
    change_url = reverse("admin:safety_risknoticeversion_change", args=[old.pk])
    admin_client.post(change_url, {"version": "renamed", "body": "Replacement"})
    stored = RiskNoticeVersion.objects.get(pk=old.pk)
    assert stored.version == old.version
    assert stored.body == old.body
    delete_url = reverse("admin:safety_risknoticeversion_delete", args=[old.pk])
    assert admin_client.post(delete_url, {"post": "yes"}).status_code == 403
