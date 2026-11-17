from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from apps.accounts.selectors import is_verified_active_member
from apps.safety.services import current_risk_notice

from .forms import EventCancellationForm, EventRegistrationForm
from .models import Event, EventRegistration
from .services import cancel_event_registration, register_for_event

PANEL_TEMPLATE = "events/includes/registration_panel.html"
_UNSET = object()


def _is_htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true"


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
    notice=_UNSET,
    registration=_UNSET,
    registration_form=None,
    registration_error="",
    cancellation_form=None,
    cancellation_error="",
    open_dialog="",
    focus_status=False,
):
    """Build the panel context; pass ``notice``/``registration`` when known.

    ``open_dialog`` names the dialog x-ref to re-open after a failed submission;
    ``focus_status`` moves focus to the panel status after an HTMX update.
    """
    if notice is _UNSET:
        notice = current_risk_notice()
    if registration is _UNSET:
        registration = _active_registration(request.user, event)
    registration_available = event.accepts_registration(
        notice_available=notice is not None
    )
    is_member = is_verified_active_member(request.user)
    if registration_form is None and notice is not None:
        registration_form = EventRegistrationForm(initial={"risk_notice_id": notice.pk})
    if cancellation_form is None:
        cancellation_form = EventCancellationForm()
    return {
        "event": event,
        "registration": registration,
        "registration_available": registration_available,
        "can_register": registration_available and registration is None and is_member,
        "can_cancel": event.accepts_cancellation()
        and registration is not None
        and is_member,
        "current_notice": notice,
        "notice_text": notice.body.strip() if notice is not None else "",
        "registration_form": registration_form,
        "registration_error": registration_error,
        "cancellation_form": cancellation_form,
        "cancellation_error": cancellation_error,
        "open_dialog": open_dialog,
        "focus_status": focus_status,
    }


def _render_panel(request, event):
    """HTMX success response: the refreshed panel takes focus for its new status."""
    return render(
        request,
        PANEL_TEMPLATE,
        _registration_context(request, event, focus_status=True),
    )


def _render_invalid(request, context, *, page_template):
    """Re-render a failed submission as the HTMX panel or the full page."""
    if _is_htmx(request):
        return render(request, PANEL_TEMPLATE, context)
    return render(request, page_template, context, status=400)


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
    if not is_verified_active_member(request.user):
        raise PermissionDenied

    if _active_registration(request.user, event) is not None:
        if _is_htmx(request):
            return _render_panel(request, event)
        return redirect("events:detail", slug=event.slug)

    notice = current_risk_notice()
    if not event.accepts_registration(notice_available=notice is not None):
        raise PermissionDenied("Registration is unavailable.")

    if request.method == "GET":
        return render(
            request,
            "events/event_registration_confirm.html",
            _registration_context(request, event, notice=notice, registration=None),
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
            # The notice may have changed since the page loaded; ask again.
            notice = current_risk_notice()
            if notice is not None:
                form = EventRegistrationForm(initial={"risk_notice_id": notice.pk})
        else:
            if _is_htmx(request):
                return _render_panel(request, event)
            messages.success(request, "Your registration has been recorded.")
            return redirect("events:detail", slug=event.slug)

    context = _registration_context(
        request,
        event,
        notice=notice,
        registration_form=form,
        registration_error=error,
        open_dialog="registrationDialog",
    )
    return _render_invalid(
        request, context, page_template="events/event_registration_confirm.html"
    )


@login_required
@require_http_methods(["GET", "POST"])
def event_cancel(request, slug):
    event = get_object_or_404(Event.objects.public(), slug=slug)
    if not is_verified_active_member(request.user):
        raise PermissionDenied
    if not event.accepts_cancellation():
        raise PermissionDenied("Cancellation is unavailable.")

    registration = _active_registration(request.user, event)
    if request.method == "GET":
        if registration is None:
            return redirect("events:detail", slug=event.slug)
        return render(
            request,
            "events/event_cancellation_confirm.html",
            _registration_context(request, event, registration=registration),
        )

    form = EventCancellationForm(request.POST)
    error = ""
    if form.is_valid():
        try:
            cancel_event_registration(user=request.user, event_id=event.pk)
        except ValidationError as exc:
            error = " ".join(exc.messages)
        else:
            if _is_htmx(request):
                return _render_panel(request, event)
            messages.success(request, "Your registration has been cancelled.")
            return redirect("events:detail", slug=event.slug)

    context = _registration_context(
        request,
        event,
        cancellation_form=form,
        cancellation_error=error,
        open_dialog="cancellationDialog",
    )
    return _render_invalid(
        request, context, page_template="events/event_cancellation_confirm.html"
    )
