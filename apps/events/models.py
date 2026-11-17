"""Public events managed through Django Admin."""

from datetime import date, datetime, time
from typing import ClassVar
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.validators import normalize_https_scheme, validate_https_url

DEFAULT_VENUE_TEXT = "Venue details to be confirmed"
SYDNEY = ZoneInfo("Australia/Sydney")


def sydney_midnight_today() -> datetime:
    """Start of the current Sydney calendar day, the Upcoming/Past boundary."""
    today = timezone.localdate(timezone=SYDNEY)
    return datetime.combine(today, time.min, tzinfo=SYDNEY)


class EventQuerySet(models.QuerySet):
    def public(self):
        return self.filter(is_published=True)

    def upcoming(self):
        return self.filter(ends_at__gte=sydney_midnight_today())

    def past(self):
        return self.filter(ends_at__lt=sydney_midnight_today())


class Event(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(max_length=2000)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    venue_text = models.CharField(max_length=255, default=DEFAULT_VENUE_TEXT)
    map_url = models.URLField(blank=True, validators=[validate_https_url])
    is_published = models.BooleanField(default=False)
    registration_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: ClassVar[models.Manager] = EventQuerySet.as_manager()

    class Meta:
        ordering = ("starts_at", "pk")
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                condition=models.Q(ends_at__gt=models.F("starts_at")),
                name="events_event_ends_after_start",
            ),
            models.CheckConstraint(
                condition=models.Q(map_url="")
                | models.Q(map_url__startswith="https://"),
                name="events_event_map_url_https",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def clean_fields(self, exclude=None) -> None:
        # Normalize first so whitespace-only text fails the fields' blank check.
        self._normalize_fields()
        super().clean_fields(exclude=exclude)

    def clean(self) -> None:
        super().clean()
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "End time must be after start time."})

    def save(self, *args, **kwargs) -> None:
        self._normalize_fields()
        self.full_clean()
        super().save(*args, **kwargs)

    def _normalize_fields(self) -> None:
        self.title = self.title.strip()
        self.description = self.description.strip()
        self.venue_text = self.venue_text.strip()
        self.map_url = normalize_https_scheme(self.map_url.strip())

    def is_past_on(self, local_date: date) -> bool:
        return timezone.localtime(self.ends_at, SYDNEY).date() < local_date

    @property
    def is_past(self) -> bool:
        return self.is_past_on(timezone.localdate(timezone=SYDNEY))

    @property
    def is_upcoming(self) -> bool:
        return not self.is_past

    def accepts_registration(self, *, notice_available: bool) -> bool:
        """UI-level registration availability; the service rechecks under lock."""
        return bool(self.registration_open and self.is_upcoming and notice_available)

    def accepts_cancellation(self) -> bool:
        """UI-level cancellation availability; the service rechecks under lock."""
        return bool(
            settings.RISK_NOTICE_DRAFT_VISIBLE
            and self.registration_open
            and self.is_upcoming
        )


class EventRegistration(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "registered", "Registered"
        CANCELLED = "cancelled", "Cancelled"

    event = models.ForeignKey(
        Event, on_delete=models.PROTECT, related_name="registrations"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_registrations",
    )
    risk_notice = models.ForeignKey(
        "safety.RiskNoticeVersion", on_delete=models.PROTECT
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.REGISTERED
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    risk_notice_accepted_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["event", "user"],
                condition=models.Q(status="registered"),
                name="events_one_active_registration",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(status="registered", cancelled_at__isnull=True)
                    | models.Q(status="cancelled", cancelled_at__isnull=False)
                ),
                name="events_registration_valid_status",
            ),
        ]
