from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from apps.safety.services import current_risk_notice

from .forms import EventCancellationForm, EventRegistrationForm
from .models import Event, EventRegistration
from .services import cancel_event_registration, register_for_event


def _is_verified_member(user) -> bool:
    return bool(
        user.is_authenticated
        and user.is_active
        and EmailAddress.objects.filter(user=user, verified=True).exists()
    )


def _active_registration(user, event):
    if not user.is_authenticated:
        return None
    return EventRegistration.objects.filter(
        event=event,
        user=user,
        status=EventRegistration.Status.REGISTERED,
    ).first()


def _registration_context(
    request,
    event,
    *,
    registration_form=None,
    registration_error="",
    open_dialog=False,
    cancellation_form=None,
    cancellation_error="",
    open_cancel_dialog=False,
):
    registration = _active_registration(request.user, event)
    notice = current_risk_notice()
    registration_available = bool(
        event.registration_open and event.is_upcoming and notice is not None
    )
    cancellation_available = bool(
        settings.RISK_NOTICE_DRAFT_VISIBLE
        and event.registration_open
        and event.is_upcoming
    )
    if registration_form is None and notice is not None:
        registration_form = EventRegistrationForm(initial={"risk_notice_id": notice.pk})
    if cancellation_form is None:
        cancellation_form = EventCancellationForm()
    return {
        "event": event,
        "registration": registration,
        "registration_available": registration_available,
        "can_register": registration_available
        and registration is None
        and _is_verified_member(request.user),
        "can_cancel": cancellation_available
        and registration is not None
        and _is_verified_member(request.user),
        "current_notice": notice,
        "notice_text": notice.body.strip() if notice is not None else "",
        "registration_form": registration_form,
        "registration_error": registration_error,
        "open_dialog": open_dialog,
        "cancellation_form": cancellation_form,
        "cancellation_error": cancellation_error,
        "open_cancel_dialog": open_cancel_dialog,
    }


@require_GET
def event_list(request):
    selected = request.GET.get("view", "upcoming")
    if selected not in {"upcoming", "past"}:
        selected = "upcoming"
    events = Event.objects.public()
    if selected == "past":
        events = events.past().order_by("-ends_at", "-pk")
    else:
        events = events.upcoming().order_by("starts_at", "pk")
    return render(
        request,
        "events/event_list.html",
        {
            "events": events,
            "selected": selected,
            "registration_notice_available": current_risk_notice() is not None,
        },
    )


@require_GET
def event_detail(request, slug):
    event = get_object_or_404(Event.objects.public(), slug=slug)
    return render(
        request,
        "events/event_detail.html",
        _registration_context(request, event),
    )


@login_required
@require_http_methods(["GET", "POST"])
def event_register(request, slug):
    event = get_object_or_404(Event.objects.public(), slug=slug)
    if not _is_verified_member(request.user):
        raise PermissionDenied

    registration = _active_registration(request.user, event)
    if registration is not None:
        if request.headers.get("HX-Request") == "true":
            return render(
                request,
                "events/includes/registration_panel.html",
                _registration_context(request, event),
            )
        return redirect("events:detail", slug=event.slug)

    notice = current_risk_notice()
    if not event.registration_open or event.is_past or notice is None:
        raise PermissionDenied("Registration is unavailable.")

    if request.method == "GET":
        return render(
            request,
            "events/event_registration_confirm.html",
            _registration_context(request, event),
        )

    form = EventRegistrationForm(request.POST)
    error = ""
    if form.is_valid():
        try:
            register_for_event(
                user=request.user,
                event_id=event.pk,
                risk_notice_id=form.cleaned_data["risk_notice_id"],
                accepted=form.cleaned_data["accepted"],
            )
        except ValidationError as exc:
            error = " ".join(exc.messages)
            current_notice = current_risk_notice()
            if current_notice is not None:
                form = EventRegistrationForm(
                    initial={"risk_notice_id": current_notice.pk}
                )
        else:
            if request.headers.get("HX-Request") == "true":
                return render(
                    request,
                    "events/includes/registration_panel.html",
                    _registration_context(request, event),
                )
            messages.success(request, "Your registration has been recorded.")
            return redirect("events:detail", slug=event.slug)

    context = _registration_context(
        request,
        event,
        registration_form=form,
        registration_error=error,
        open_dialog=True,
    )
    if request.headers.get("HX-Request") == "true":
        return render(request, "events/includes/registration_panel.html", context)
    return render(
        request,
        "events/event_registration_confirm.html",
        context,
        status=400,
    )


@login_required
@require_http_methods(["GET", "POST"])
def event_cancel(request, slug):
    event = get_object_or_404(Event.objects.public(), slug=slug)
    if not _is_verified_member(request.user):
        raise PermissionDenied
    if (
        not settings.RISK_NOTICE_DRAFT_VISIBLE
        or not event.registration_open
        or event.is_past
    ):
        raise PermissionDenied("Cancellation is unavailable.")

    registration = _active_registration(request.user, event)
    if request.method == "GET":
        if registration is None:
            return redirect("events:detail", slug=event.slug)
        return render(
            request,
            "events/event_cancellation_confirm.html",
            _registration_context(request, event),
        )

    form = EventCancellationForm(request.POST)
    error = ""
    if form.is_valid():
        try:
            cancel_event_registration(user=request.user, event_id=event.pk)
        except ValidationError as exc:
            error = " ".join(exc.messages)
        else:
            if request.headers.get("HX-Request") == "true":
                return render(
                    request,
                    "events/includes/registration_panel.html",
                    _registration_context(request, event),
                )
            messages.success(request, "Your registration has been cancelled.")
            return redirect("events:detail", slug=event.slug)

    context = _registration_context(
        request,
        event,
        cancellation_form=form,
        cancellation_error=error,
        open_cancel_dialog=True,
    )
    if request.headers.get("HX-Request") == "true":
        return render(request, "events/includes/registration_panel.html", context)
    return render(
        request,
        "events/event_cancellation_confirm.html",
        context,
        status=400,
    )
