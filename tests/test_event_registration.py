from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

import pytest
from allauth.account.models import EmailAddress
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, close_old_connections, transaction
from django.utils import timezone

from apps.events.models import Event, EventRegistration
from apps.events.services import cancel_event_registration, register_for_event
from apps.safety.models import RiskNoticeVersion
from apps.safety.services import activate_risk_notice

pytestmark = pytest.mark.django_db


@pytest.fixture
def registration_data(settings, django_user_model):
    settings.RISK_NOTICE_DRAFT_VISIBLE = True
    user = django_user_model.objects.create_user(
        username="registration-test", email="registration@example.test"
    )
    EmailAddress.objects.create(
        user=user, email=user.email, verified=True, primary=True
    )
    now = timezone.now()
    event = Event.objects.create(
        title="Synthetic session",
        slug="synthetic-session",
        description="Synthetic test event.",
        starts_at=now + timedelta(days=2),
        ends_at=now + timedelta(days=2, hours=1),
        is_published=True,
        registration_open=True,
    )
    notice = RiskNoticeVersion.objects.create(
        version="synthetic-v1", body="SYNTHETIC TEST ONLY\nSample."
    )
    activate_risk_notice(notice.pk)
    return user, event, notice


def register(data, **overrides):
    user, event, notice = data
    arguments = {
        "user": user,
        "event_id": event.pk,
        "risk_notice_id": notice.pk,
        "accepted": True,
    }
    arguments.update(overrides)
    return register_for_event(**arguments)


def test_registration_records_confirmation_and_is_idempotent(registration_data):
    registration = register(registration_data)
    assert register(registration_data).pk == registration.pk
    assert registration.risk_notice == registration_data[2]
    assert registration.risk_notice_accepted_at is not None
    assert registration.registered_at is not None
    assert registration.cancelled_at is None
    assert EventRegistration.objects.count() == 1


def test_database_enforces_single_active_registration(registration_data):
    first = register(registration_data)
    with pytest.raises(IntegrityError), transaction.atomic():
        EventRegistration.objects.create(
            event=first.event,
            user=first.user,
            risk_notice=first.risk_notice,
            risk_notice_accepted_at=timezone.now(),
        )


def test_cancelled_history_preserves_original_notice(registration_data):
    first = register(registration_data)
    cancelled = cancel_event_registration(
        user=registration_data[0], event_id=registration_data[1].pk
    )
    assert (
        cancel_event_registration(
            user=registration_data[0], event_id=registration_data[1].pk
        ).pk
        == cancelled.pk
    )
    newer = RiskNoticeVersion.objects.create(
        version="synthetic-v2", body="SYNTHETIC TEST ONLY\nNew sample."
    )
    activate_risk_notice(newer.pk)
    second = register(registration_data, risk_notice_id=newer.pk)
    first.refresh_from_db()
    assert first.pk != second.pk
    assert first.risk_notice == registration_data[2]
    assert second.risk_notice == newer
    assert first.cancelled_at is not None


def test_cancellation_sets_status_and_timestamp_without_deleting_history(
    registration_data,
):
    registration = register(registration_data)

    cancelled = cancel_event_registration(
        user=registration_data[0], event_id=registration_data[1].pk
    )

    assert cancelled.pk == registration.pk
    assert cancelled.status == EventRegistration.Status.CANCELLED
    assert cancelled.cancelled_at is not None
    assert cancelled.risk_notice == registration_data[2]
    assert EventRegistration.objects.count() == 1


@pytest.mark.parametrize("condition", ["closed", "past", "production"])
def test_cancellation_rejects_unavailable_event(settings, registration_data, condition):
    registration = register(registration_data)
    if condition == "closed":
        Event.objects.filter(pk=registration_data[1].pk).update(registration_open=False)
    elif condition == "past":
        now = timezone.now()
        Event.objects.filter(pk=registration_data[1].pk).update(
            starts_at=now - timedelta(days=4), ends_at=now - timedelta(days=3)
        )
    else:
        settings.RISK_NOTICE_DRAFT_VISIBLE = False

    expected_error = PermissionDenied if condition == "production" else ValidationError
    with pytest.raises(expected_error):
        cancel_event_registration(
            user=registration_data[0], event_id=registration_data[1].pk
        )

    registration.refresh_from_db()
    assert registration.status == EventRegistration.Status.REGISTERED
    assert registration.cancelled_at is None


def test_database_rejects_invalid_status_and_cancel_time(registration_data):
    first = register(registration_data)
    with pytest.raises(IntegrityError), transaction.atomic():
        EventRegistration.objects.filter(pk=first.pk).update(status="cancelled")
    with pytest.raises(IntegrityError), transaction.atomic():
        EventRegistration.objects.filter(pk=first.pk).update(status="unknown")


def test_registration_rejects_stale_and_unconfirmed_notice(registration_data):
    user, event, notice = registration_data
    with pytest.raises(ValidationError):
        register(registration_data, accepted=False)
    newer = RiskNoticeVersion.objects.create(version="unmarked", body="Test content")
    activate_risk_notice(newer.pk)
    with pytest.raises(ValidationError):
        register(registration_data, risk_notice_id=notice.pk)
    registration = register(registration_data, risk_notice_id=newer.pk)
    assert registration.risk_notice == newer
    assert EventRegistration.objects.filter(user=user, event=event).count() == 1


def test_disabled_environment_and_ineligible_member_are_rejected(
    settings, registration_data
):
    user, _, _ = registration_data
    settings.RISK_NOTICE_DRAFT_VISIBLE = False
    with pytest.raises(PermissionDenied):
        register(registration_data)
    settings.RISK_NOTICE_DRAFT_VISIBLE = True
    EmailAddress.objects.filter(user=user).update(verified=False)
    with pytest.raises(PermissionDenied):
        register(registration_data)
    assert not EventRegistration.objects.exists()


@pytest.mark.parametrize("field", ["registration_open", "is_published"])
def test_closed_or_private_event_is_rejected(registration_data, field):
    Event.objects.filter(pk=registration_data[1].pk).update(**{field: False})
    with pytest.raises(ValidationError):
        register(registration_data)
    assert not EventRegistration.objects.exists()


def test_past_event_is_rejected(registration_data):
    now = timezone.now()
    Event.objects.filter(pk=registration_data[1].pk).update(
        starts_at=now - timedelta(days=4), ends_at=now - timedelta(days=3)
    )
    with pytest.raises(ValidationError):
        register(registration_data)
    assert not EventRegistration.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_concurrent_submissions_create_one_active_registration(registration_data):
    barrier = Barrier(2)

    def submit():
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            return register(registration_data).pk
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        ids = list(executor.map(lambda _: submit(), range(2)))
    assert ids[0] == ids[1]
    assert EventRegistration.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_concurrent_cancellations_are_idempotent(registration_data):
    registration = register(registration_data)
    barrier = Barrier(2)

    def cancel():
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            return cancel_event_registration(
                user=registration_data[0], event_id=registration_data[1].pk
            ).pk
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        ids = list(executor.map(lambda _: cancel(), range(2)))

    registration.refresh_from_db()
    assert ids == [registration.pk, registration.pk]
    assert registration.status == EventRegistration.Status.CANCELLED
    assert registration.cancelled_at is not None
    assert EventRegistration.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_registration_and_notice_switch_are_serialized(registration_data):
    new_notice = RiskNoticeVersion.objects.create(
        version="synthetic-v2", body="SYNTHETIC TEST ONLY\nUpdated sample."
    )
    barrier = Barrier(2)

    def submit():
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                return register(registration_data).pk
            except ValidationError:
                return None
        finally:
            close_old_connections()

    def switch():
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            activate_risk_notice(new_notice.pk)
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        submitted = executor.submit(submit)
        switched = executor.submit(switch)
        registration_id = submitted.result(timeout=20)
        switched.result(timeout=20)
    new_notice.refresh_from_db()
    if registration_id is not None:
        registration = EventRegistration.objects.get(pk=registration_id)
        assert registration.risk_notice_id == registration_data[2].pk
        assert registration.risk_notice_accepted_at <= new_notice.activated_at
    else:
        assert not EventRegistration.objects.exists()
