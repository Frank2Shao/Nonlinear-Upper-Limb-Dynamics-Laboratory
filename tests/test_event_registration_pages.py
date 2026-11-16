from datetime import timedelta

import pytest
from allauth.account.models import EmailAddress
from django.urls import reverse
from django.utils import timezone

from apps.events.models import Event, EventRegistration
from apps.safety.models import RiskNoticeVersion
from apps.safety.services import activate_risk_notice

pytestmark = pytest.mark.django_db

RISK_NOTICE_TEXT = """SYNTHETIC TEST ONLY
Participation in armwrestling is voluntary. Armwrestling involves physical exertion against an opponent. Injuries can occur even when safety rules are followed and the activity is supervised. Possible injuries include muscle strains, tendon or ligament injuries, joint sprains or dislocations, and fractures.

Before taking part, consider any previous injuries or health conditions that may affect your ability to participate safely. Examples include previous shoulder, elbow or wrist injuries, other musculoskeletal conditions, cardiovascular or cerebrovascular disease, osteoporosis, and neurological conditions. If you are unsure whether you should take part, seek advice from a health professional before participating.

Attend the safety briefing before taking part and participate under the supervision of the person in charge. You may stop at any time. Stop immediately if you experience pain, numbness, dizziness or other discomfort, or if the person in charge asks you to stop. Tell the person in charge if you feel unwell or are injured.

By confirming my registration before taking part in this event, I confirm that I have read and understood the risk notice above, had an opportunity to ask questions, understand the risks of injury, and choose to participate voluntarily. I agree to follow the activity safety rules and safety directions given on site. This acknowledgement does not exclude or limit any rights or remedies available to me under law."""


@pytest.fixture
def registration_page_data(settings, django_user_model):
    settings.RISK_NOTICE_DRAFT_VISIBLE = True
    user = django_user_model.objects.create_user(
        username="page-member",
        email="page-member@example.test",
        password="test-password",
        first_name="Private",
        last_name="Registrant",
        is_usyd_student=True,
        usu_id="00123456",
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True,
    )
    start = timezone.now() + timedelta(days=2)
    event = Event.objects.create(
        title="Registration session",
        slug="registration-session",
        description="Synthetic registration event.",
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
    return user, event, notice


def test_verified_member_opens_confirmation_with_approved_source_text(
    client, registration_page_data
):
    user, event, notice = registration_page_data
    client.force_login(user)

    detail = client.get(reverse("events:detail", args=[event.slug]))
    assert detail.status_code == 200
    assert "Register" in detail.content.decode()
    assert "Participation in armwrestling is voluntary." in detail.content.decode()

    confirmation = client.get(reverse("events:register", args=[event.slug]))
    content = confirmation.content.decode()
    assert confirmation.status_code == 200
    assert notice.version in content
    assert content.count("SYNTHETIC TEST ONLY") == 1
    assert "By confirming my registration" in content
    assert "By signing below" not in content
    assert "Event name:" not in content
    assert "Participant Signature" not in content


def test_normal_post_registers_current_member_and_is_idempotent(
    client, registration_page_data
):
    user, event, notice = registration_page_data
    client.force_login(user)
    url = reverse("events:register", args=[event.slug])
    payload = {"risk_notice_id": notice.pk, "accepted": "true"}

    first = client.post(url, payload)
    second = client.post(url, payload)

    assert first.status_code == 302
    assert first.url == reverse("events:detail", args=[event.slug])
    assert second.status_code == 302
    registration = EventRegistration.objects.get(event=event, user=user)
    assert registration.risk_notice == notice
    assert registration.risk_notice_accepted_at is not None
    assert EventRegistration.objects.count() == 1
    detail = client.get(reverse("events:detail", args=[event.slug])).content.decode()
    assert "Registered" in detail
    assert ">Register</a>" not in detail


def test_htmx_post_replaces_registration_panel(client, registration_page_data):
    user, event, notice = registration_page_data
    client.force_login(user)

    response = client.post(
        reverse("events:register", args=[event.slug]),
        {"risk_notice_id": notice.pk, "accepted": "true"},
        headers={"HX-Request": "true"},
    )

    content = response.content.decode()
    assert response.status_code == 200
    assert 'id="event-registration"' in content
    assert "Registered" in content
    assert "<html" not in content


def test_member_cancels_idempotently_and_can_register_again(
    client, registration_page_data
):
    user, event, first_notice = registration_page_data
    client.force_login(user)
    register_url = reverse("events:register", args=[event.slug])
    cancel_url = reverse("events:cancel", args=[event.slug])
    client.post(
        register_url,
        {"risk_notice_id": first_notice.pk, "accepted": "true"},
    )

    cancellation = client.post(cancel_url, {"confirmed": "true"})
    repeated = client.post(cancel_url, {"confirmed": "true"})

    assert cancellation.status_code == 302
    assert cancellation.url == reverse("events:detail", args=[event.slug])
    assert repeated.status_code == 302
    first_registration = EventRegistration.objects.get(event=event, user=user)
    assert first_registration.status == EventRegistration.Status.CANCELLED
    assert first_registration.cancelled_at is not None
    detail = client.get(reverse("events:detail", args=[event.slug])).content.decode()
    assert ">Register</a>" in detail
    assert "Cancel registration" not in detail

    second_notice = RiskNoticeVersion.objects.create(
        version="synthetic-en-v2",
        body=RISK_NOTICE_TEXT.replace(
            "Participation in armwrestling is voluntary.",
            "Participation in armwrestling remains voluntary.",
        ),
    )
    activate_risk_notice(second_notice.pk)
    second = client.post(
        register_url,
        {"risk_notice_id": second_notice.pk, "accepted": "true"},
    )

    assert second.status_code == 302
    registrations = EventRegistration.objects.filter(event=event, user=user).order_by(
        "pk"
    )
    assert registrations.count() == 2
    assert registrations[0].risk_notice == first_notice
    assert registrations[0].status == EventRegistration.Status.CANCELLED
    assert registrations[1].risk_notice == second_notice
    assert registrations[1].status == EventRegistration.Status.REGISTERED


def test_htmx_cancellation_replaces_panel(client, registration_page_data):
    user, event, notice = registration_page_data
    client.force_login(user)
    client.post(
        reverse("events:register", args=[event.slug]),
        {"risk_notice_id": notice.pk, "accepted": "true"},
    )

    response = client.post(
        reverse("events:cancel", args=[event.slug]),
        {"confirmed": "true"},
        headers={"HX-Request": "true"},
    )

    content = response.content.decode()
    assert response.status_code == 200
    assert 'id="event-registration"' in content
    assert ">Register</a>" in content
    assert "Registered" not in content
    assert "<html" not in content


def test_stale_notice_requires_confirmation_of_new_version(
    client, registration_page_data
):
    user, event, old_notice = registration_page_data
    client.force_login(user)
    new_notice = RiskNoticeVersion.objects.create(
        version="synthetic-en-v2",
        body=RISK_NOTICE_TEXT.replace(
            "\n",
            "\r\n",
        ).replace(
            "Participation in armwrestling is voluntary.",
            "Participation in armwrestling remains voluntary.",
        ),
    )
    activate_risk_notice(new_notice.pk)

    response = client.post(
        reverse("events:register", args=[event.slug]),
        {"risk_notice_id": old_notice.pk, "accepted": "true"},
    )

    content = response.content.decode()
    assert response.status_code == 400
    assert "Please review the current Risk Notice." in content
    assert new_notice.version in content
    assert "Participation in armwrestling remains voluntary." in content
    assert content.count("SYNTHETIC TEST ONLY") == 1
    assert f'value="{new_notice.pk}"' in content
    assert not EventRegistration.objects.exists()


@pytest.mark.parametrize("condition", ["closed", "past", "production"])
def test_unavailable_registration_has_no_button_and_rejects_direct_access(
    client, registration_page_data, settings, condition
):
    user, event, _ = registration_page_data
    client.force_login(user)
    if condition == "closed":
        Event.objects.filter(pk=event.pk).update(registration_open=False)
    elif condition == "past":
        now = timezone.now()
        Event.objects.filter(pk=event.pk).update(
            starts_at=now - timedelta(days=3),
            ends_at=now - timedelta(days=2),
        )
    else:
        settings.RISK_NOTICE_DRAFT_VISIBLE = False

    detail = client.get(reverse("events:detail", args=[event.slug])).content.decode()
    assert ">Register</a>" not in detail
    assert client.get(reverse("events:register", args=[event.slug])).status_code == 403
    assert not EventRegistration.objects.exists()


@pytest.mark.parametrize("condition", ["closed", "past", "production"])
def test_unavailable_cancellation_has_no_button_and_rejects_direct_access(
    client, registration_page_data, settings, condition
):
    user, event, notice = registration_page_data
    client.force_login(user)
    client.post(
        reverse("events:register", args=[event.slug]),
        {"risk_notice_id": notice.pk, "accepted": "true"},
    )
    if condition == "closed":
        Event.objects.filter(pk=event.pk).update(registration_open=False)
    elif condition == "past":
        now = timezone.now()
        Event.objects.filter(pk=event.pk).update(
            starts_at=now - timedelta(days=3),
            ends_at=now - timedelta(days=2),
        )
    else:
        settings.RISK_NOTICE_DRAFT_VISIBLE = False

    detail = client.get(reverse("events:detail", args=[event.slug])).content.decode()
    assert "Cancel registration" not in detail
    assert client.get(reverse("events:cancel", args=[event.slug])).status_code == 403
    registration = EventRegistration.objects.get(event=event, user=user)
    assert registration.status == EventRegistration.Status.REGISTERED


def test_cancellation_requires_confirmation(client, registration_page_data):
    user, event, notice = registration_page_data
    client.force_login(user)
    client.post(
        reverse("events:register", args=[event.slug]),
        {"risk_notice_id": notice.pk, "accepted": "true"},
    )

    response = client.post(reverse("events:cancel", args=[event.slug]), {})

    assert response.status_code == 400
    assert "Please confirm that you want to cancel" in response.content.decode()
    registration = EventRegistration.objects.get(event=event, user=user)
    assert registration.status == EventRegistration.Status.REGISTERED


def test_anonymous_and_unconfirmed_submissions_do_not_register(
    client, registration_page_data
):
    user, event, notice = registration_page_data
    url = reverse("events:register", args=[event.slug])
    anonymous = client.get(url)
    assert anonymous.status_code == 302
    assert reverse("account_login") in anonymous.url

    client.force_login(user)
    response = client.post(url, {"risk_notice_id": notice.pk})
    assert response.status_code == 400
    assert "Please correct the registration form." in response.content.decode()
    assert not EventRegistration.objects.exists()


def test_public_and_other_member_views_do_not_expose_registration_history(
    client, registration_page_data, django_user_model
):
    owner, event, first_notice = registration_page_data
    register_url = reverse("events:register", args=[event.slug])
    cancel_url = reverse("events:cancel", args=[event.slug])
    client.force_login(owner)
    client.post(
        register_url,
        {"risk_notice_id": first_notice.pk, "accepted": "true"},
    )
    client.post(cancel_url, {"confirmed": "true"})

    current_notice = RiskNoticeVersion.objects.create(
        version="synthetic-private-current",
        body=RISK_NOTICE_TEXT.replace(
            "Participation in armwrestling is voluntary.",
            "Participation in armwrestling remains voluntary.",
        ),
    )
    activate_risk_notice(current_notice.pk)
    client.post(
        register_url,
        {"risk_notice_id": current_notice.pk, "accepted": "true"},
    )

    private_values = (
        owner.get_full_name(),
        owner.username,
        owner.email,
        owner.usu_id,
        first_notice.version,
    )
    client.logout()
    for path in (
        reverse("home"),
        reverse("events:list"),
        reverse("events:detail", args=[event.slug]),
    ):
        content = client.get(path).content.decode()
        for private_value in private_values:
            assert private_value not in content

    other_member = django_user_model.objects.create_user(
        username="other-event-member",
        email="other-event-member@example.test",
        password="test-password",
    )
    EmailAddress.objects.create(
        user=other_member,
        email=other_member.email,
        verified=True,
        primary=True,
    )
    client.force_login(other_member)
    detail = client.get(reverse("events:detail", args=[event.slug])).content.decode()
    assert ">Register</a>" in detail
    assert "Cancel registration" not in detail
    assert "Registered" not in detail
    for private_value in private_values:
        assert private_value not in detail

    cancellation = client.post(cancel_url, {"confirmed": "true"})
    assert cancellation.status_code == 400
    owner_registration = EventRegistration.objects.get(
        event=event,
        user=owner,
        status=EventRegistration.Status.REGISTERED,
    )
    assert owner_registration.risk_notice == current_notice
    assert owner_registration.cancelled_at is None
