from datetime import date, datetime

import pytest
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone

from apps.events.admin import EventAdmin
from apps.events.models import DEFAULT_VENUE_TEXT, Event

pytestmark = pytest.mark.django_db


def aware(year, month, day, hour):
    return timezone.make_aware(datetime(year, month, day, hour))


def event_values(**overrides):
    values = {
        "title": "Training Session",
        "slug": "training-session",
        "description": "Synthetic event used for automated testing.",
        "starts_at": aware(2026, 12, 1, 15),
        "ends_at": aware(2026, 12, 1, 19),
    }
    values.update(overrides)
    return values


def test_event_defaults_and_public_queryset():
    private = Event.objects.create(**event_values())
    public = Event.objects.create(
        **event_values(
            title="Public Session",
            slug="public-session",
            is_published=True,
            registration_open=True,
        )
    )
    assert str(private) == "Training Session"
    assert private.venue_text == DEFAULT_VENUE_TEXT
    assert private.map_url == ""
    assert not private.is_published
    assert not private.registration_open
    assert list(Event.objects.public()) == [public]


@pytest.mark.parametrize(
    ("ends_at", "message"),
    [
        (aware(2026, 12, 1, 15), "End time must be after start time."),
        (aware(2026, 12, 1, 14), "End time must be after start time."),
    ],
)
def test_event_rejects_invalid_time_range(ends_at, message):
    with pytest.raises(ValidationError, match=message):
        Event.objects.create(**event_values(ends_at=ends_at))


def test_database_rejects_invalid_time_range():
    event = Event.objects.create(**event_values())
    with pytest.raises(IntegrityError), transaction.atomic():
        Event.objects.filter(pk=event.pk).update(ends_at=event.starts_at)


def test_event_accepts_only_https_map_links():
    event = Event.objects.create(
        **event_values(map_url="https://maps.google.com/?q=synthetic")
    )
    assert event.map_url.startswith("https://")
    with pytest.raises(ValidationError):
        Event.objects.create(
            **event_values(slug="insecure-map", map_url="http://maps.google.com/")
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        Event.objects.filter(pk=event.pk).update(map_url="http://maps.google.com/")


def test_event_normalizes_text_fields():
    event = Event.objects.create(
        **event_values(
            title="  Training Session  ",
            description="  Synthetic description.  ",
            venue_text="  Venue details to be confirmed  ",
            map_url="  https://maps.google.com/?q=synthetic  ",
        )
    )
    assert event.title == "Training Session"
    assert event.description == "Synthetic description."
    assert event.venue_text == DEFAULT_VENUE_TEXT
    assert event.map_url == "https://maps.google.com/?q=synthetic"


def test_event_moves_to_past_after_next_local_midnight():
    event = Event(**event_values())
    assert not event.is_past_on(date(2026, 12, 1))
    assert event.is_past_on(date(2026, 12, 2))


def test_event_admin_configuration():
    assert EventAdmin.list_display == (
        "title",
        "starts_at",
        "ends_at",
        "is_published",
        "registration_open",
    )
    assert EventAdmin.prepopulated_fields == {"slug": ("title",)}
    assert EventAdmin.readonly_fields == ("created_at", "updated_at")


def test_authorized_staff_can_manage_events(client, django_user_model):
    staff = django_user_model.objects.create_user(
        username="event-editor",
        email="event-editor@example.test",
        password="synthetic-password",
        is_staff=True,
    )
    staff.user_permissions.add(
        *Permission.objects.filter(
            content_type__app_label="events",
            codename__in=("add_event", "change_event", "view_event"),
        )
    )
    client.force_login(staff)
    add_url = reverse("admin:events_event_add")
    response = client.post(
        add_url,
        {
            "title": "Training Session",
            "slug": "training-session",
            "description": "Synthetic event used for automated testing.",
            "venue_text": DEFAULT_VENUE_TEXT,
            "starts_at_0": "2026-12-01",
            "starts_at_1": "15:00:00",
            "ends_at_0": "2026-12-01",
            "ends_at_1": "19:00:00",
            "map_url": "https://maps.google.com/?q=synthetic",
            "is_published": "on",
            "registration_open": "on",
        },
    )
    assert response.status_code == 302, response.context["adminform"].form.errors
    event = Event.objects.get(slug="training-session")
    assert event.is_published
    assert event.registration_open


def test_staff_without_event_permission_cannot_access_admin(client, django_user_model):
    staff = django_user_model.objects.create_user(
        username="unrelated-staff",
        email="unrelated-staff@example.test",
        password="synthetic-password",
        is_staff=True,
    )
    client.force_login(staff)
    assert client.get(reverse("admin:events_event_changelist")).status_code == 403
