"""Public events managed through Django Admin."""

from datetime import date, datetime, time
from typing import ClassVar
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone

DEFAULT_VENUE_TEXT = "Venue details to be confirmed"
SYDNEY = ZoneInfo("Australia/Sydney")


def validate_https_url(value: str) -> None:
    if not value:
        return
    URLValidator(schemes=["https"])(value)
    if not value.lower().startswith("https://"):
        raise ValidationError("Use an HTTPS URL.")


class EventQuerySet(models.QuerySet):
    def public(self):
        return self.filter(is_published=True)

    def upcoming(self):
        today = timezone.localdate(timezone=SYDNEY)
        midnight = datetime.combine(today, time.min, tzinfo=SYDNEY)
        return self.filter(ends_at__gte=midnight)

    def past(self):
        today = timezone.localdate(timezone=SYDNEY)
        midnight = datetime.combine(today, time.min, tzinfo=SYDNEY)
        return self.filter(ends_at__lt=midnight)


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

    def clean(self) -> None:
        self._normalize_fields()
        super().clean()
        if not self.title:
            raise ValidationError({"title": "Enter an event title."})
        if not self.description:
            raise ValidationError({"description": "Enter an event description."})
        if not self.venue_text:
            raise ValidationError({"venue_text": "Enter venue information."})
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
        self.map_url = self.map_url.strip()
        if self.map_url.lower().startswith("https://"):
            self.map_url = f"https://{self.map_url[8:]}"

    def is_past_on(self, local_date: date) -> bool:
        return timezone.localtime(self.ends_at, SYDNEY).date() < local_date

    @property
    def is_past(self) -> bool:
        return self.is_past_on(timezone.localdate(timezone=SYDNEY))

    @property
    def is_upcoming(self) -> bool:
        return not self.is_past


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
