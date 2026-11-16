"""Transactional registration foundation for synthetic development data."""

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.safety.models import RiskNoticeVersion

from .models import Event, EventRegistration


@transaction.atomic
def register_for_event(*, user, event_id: int, risk_notice_id: int, accepted: bool):
    """Record an explicit acknowledgement of the current synthetic notice."""
    if not settings.RISK_NOTICE_DRAFT_VISIBLE:
        raise PermissionDenied("Registration is unavailable.")
    if not getattr(user, "is_authenticated", False) or not user.pk:
        raise PermissionDenied("A verified active account is required.")

    event = Event.objects.select_for_update().get(pk=event_id)
    member = get_user_model().objects.select_for_update().get(pk=user.pk)
    if (
        not member.is_active
        or not EmailAddress.objects.filter(user=member, verified=True).exists()
    ):
        raise PermissionDenied("A verified active account is required.")
    if not event.is_published or not event.registration_open or event.is_past:
        raise ValidationError("Registration is closed.")
    if accepted is not True:
        raise ValidationError("Risk Notice confirmation is required.")

    # Match activation's lock order, so the accepted version cannot change mid-write.
    versions = list(RiskNoticeVersion.objects.select_for_update().order_by("pk"))
    current = next((version for version in versions if version.is_current), None)
    if current is None or current.pk != risk_notice_id:
        raise ValidationError("Please review the current Risk Notice.")

    existing = EventRegistration.objects.filter(
        event=event, user=member, status=EventRegistration.Status.REGISTERED
    ).first()
    if existing:
        return existing
    return EventRegistration.objects.create(
        event=event,
        user=member,
        risk_notice=current,
        risk_notice_accepted_at=timezone.now(),
    )


@transaction.atomic
def cancel_event_registration(*, user, event_id: int):
    """Cancel the current registration while retaining its history."""
    if not settings.RISK_NOTICE_DRAFT_VISIBLE:
        raise PermissionDenied("Cancellation is unavailable.")
    if not getattr(user, "is_authenticated", False) or not user.pk:
        raise PermissionDenied("A verified active account is required.")

    event = Event.objects.select_for_update().get(pk=event_id)
    member = get_user_model().objects.select_for_update().get(pk=user.pk)
    if (
        not member.is_active
        or not EmailAddress.objects.filter(user=member, verified=True).exists()
    ):
        raise PermissionDenied("A verified active account is required.")
    if not event.is_published or not event.registration_open or event.is_past:
        raise ValidationError("Cancellation is unavailable.")

    registrations = EventRegistration.objects.select_for_update().filter(
        event=event,
        user=member,
    )
    active = registrations.filter(status=EventRegistration.Status.REGISTERED).first()
    if active is not None:
        active.status = EventRegistration.Status.CANCELLED
        active.cancelled_at = timezone.now()
        active.save(update_fields=["status", "cancelled_at"])
        return active

    cancelled = (
        registrations.filter(status=EventRegistration.Status.CANCELLED)
        .order_by("-cancelled_at", "-pk")
        .first()
    )
    if cancelled is not None:
        return cancelled
    raise ValidationError("No active registration was found.")
