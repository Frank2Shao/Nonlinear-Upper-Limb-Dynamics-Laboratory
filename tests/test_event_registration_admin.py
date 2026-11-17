from datetime import timedelta

import pytest
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone

from apps.events.admin import EventRegistrationAdmin
from apps.events.models import Event, EventRegistration
from apps.safety.models import RiskNoticeVersion
from tests import factories
from tests.privacy import assert_no_private_values

pytestmark = pytest.mark.django_db
PASSWORD = "A-valid-password-2026"


def create_user(*, username: str, **extra_fields):
    return factories.create_user(
        username,
        email=f"{username}@example.test",
        password=PASSWORD,
        **extra_fields,
    )


def grant_permission(user, codename: str):
    user.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="events",
            codename=codename,
        )
    )
    return user


def create_registration_history(django_user_model):
    member = create_user(
        username="roster-member",
        first_name="Synthetic",
        last_name="Member",
        is_usyd_student=True,
        usu_id="00123456",
    )
    now = timezone.now()
    event = Event.objects.create(
        title="Synthetic roster session",
        slug="synthetic-roster-session",
        description="Synthetic event used to test the private admin roster.",
        starts_at=now + timedelta(days=2),
        ends_at=now + timedelta(days=2, hours=1),
        is_published=True,
        registration_open=True,
    )
    first_notice = RiskNoticeVersion.objects.create(
        version="synthetic-roster-v1",
        body="SYNTHETIC TEST ONLY\nFirst roster version.",
    )
    current_notice = RiskNoticeVersion.objects.create(
        version="synthetic-roster-v2",
        body="SYNTHETIC TEST ONLY\nCurrent roster version.",
    )
    cancelled = EventRegistration.objects.create(
        event=event,
        user=member,
        risk_notice=first_notice,
        status=EventRegistration.Status.CANCELLED,
        risk_notice_accepted_at=now - timedelta(hours=2),
        cancelled_at=now - timedelta(hours=1),
    )
    active = EventRegistration.objects.create(
        event=event,
        user=member,
        risk_notice=current_notice,
        risk_notice_accepted_at=now,
    )
    return member, event, cancelled, active


def test_registration_admin_is_read_only_and_uses_standard_view_permission():
    model_admin = admin.site._registry[EventRegistration]

    assert isinstance(model_admin, EventRegistrationAdmin)
    assert model_admin.actions == ()
    assert model_admin.has_add_permission(None) is False
    assert model_admin.has_change_permission(None) is False
    assert model_admin.has_delete_permission(None) is False
    assert not EventRegistration._meta.permissions


def test_regular_member_cannot_access_registration_roster(client, django_user_model):
    member, _event, _cancelled, active = create_registration_history(django_user_model)
    client.force_login(member)

    list_response = client.get(reverse("admin:events_eventregistration_changelist"))
    detail_response = client.get(
        reverse("admin:events_eventregistration_change", args=(active.pk,))
    )

    assert list_response.status_code == 302
    assert reverse("admin:login") in list_response.url
    assert detail_response.status_code == 302
    assert reverse("admin:login") in detail_response.url


def test_staff_without_roster_permission_cannot_access(client, django_user_model):
    staff = create_user(username="unpermitted-roster-staff", is_staff=True)
    _member, _event, _cancelled, active = create_registration_history(django_user_model)
    client.force_login(staff)

    assert (
        client.get(reverse("admin:events_eventregistration_changelist")).status_code
        == 403
    )
    assert (
        client.get(
            reverse("admin:events_eventregistration_change", args=(active.pk,))
        ).status_code
        == 403
    )


def test_event_editor_permission_does_not_grant_roster_access(
    client, django_user_model
):
    staff = grant_permission(
        create_user(username="event-editor-only", is_staff=True),
        "change_event",
    )
    create_registration_history(django_user_model)
    client.force_login(staff)

    response = client.get(reverse("admin:events_eventregistration_changelist"))

    assert response.status_code == 403


def test_authorized_staff_can_view_current_and_historical_registration_data(
    client, django_user_model
):
    staff = grant_permission(
        create_user(username="roster-viewer", is_staff=True),
        "view_eventregistration",
    )
    member, event, cancelled, active = create_registration_history(django_user_model)
    client.force_login(staff)

    response = client.get(reverse("admin:events_eventregistration_changelist"))

    assert response.status_code == 200
    content = response.content.decode()
    assert event.title in content
    assert "Synthetic Member" in content
    assert member.username in content
    assert member.email in content
    assert member.usu_id in content
    assert cancelled.risk_notice.version in content
    assert active.risk_notice.version in content
    assert "Cancelled" in content
    assert "Registered" in content


def test_authorized_staff_has_read_only_detail_and_cannot_forge_changes(
    client, django_user_model
):
    staff = grant_permission(
        create_user(username="readonly-roster-viewer", is_staff=True),
        "view_eventregistration",
    )
    _member, _event, _cancelled, active = create_registration_history(django_user_model)
    detail_url = reverse("admin:events_eventregistration_change", args=(active.pk,))
    client.force_login(staff)

    detail_response = client.get(detail_url)
    post_response = client.post(
        detail_url,
        data={
            "status": EventRegistration.Status.CANCELLED,
            "cancelled_at": timezone.now().isoformat(),
            "_save": "Save",
        },
    )
    add_response = client.get(reverse("admin:events_eventregistration_add"))
    delete_response = client.get(
        reverse("admin:events_eventregistration_delete", args=(active.pk,))
    )
    active.refresh_from_db()

    assert detail_response.status_code == 200
    assert detail_response.context["show_save"] is False
    assert post_response.status_code == 403
    assert add_response.status_code == 403
    assert delete_response.status_code == 403
    assert active.status == EventRegistration.Status.REGISTERED
    assert active.cancelled_at is None


def test_superuser_can_view_roster_but_cannot_modify_it(client, django_user_model):
    superuser = django_user_model.objects.create_superuser(
        username="roster-superuser",
        email="roster-superuser@example.test",
        password=PASSWORD,
    )
    _member, _event, _cancelled, active = create_registration_history(django_user_model)
    client.force_login(superuser)

    list_response = client.get(reverse("admin:events_eventregistration_changelist"))
    detail_response = client.get(
        reverse("admin:events_eventregistration_change", args=(active.pk,))
    )

    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert detail_response.context["show_save"] is False


def test_public_event_page_does_not_expose_roster_or_history(client, django_user_model):
    member, event, cancelled, active = create_registration_history(django_user_model)

    response = client.get(reverse("events:detail", args=(event.slug,)))
    content = response.content.decode()

    assert response.status_code == 200
    assert_no_private_values(
        content,
        (
            member.get_full_name(),
            member.email,
            member.usu_id,
            cancelled.risk_notice.version,
            active.risk_notice.version,
        ),
        context="Public event detail",
    )
