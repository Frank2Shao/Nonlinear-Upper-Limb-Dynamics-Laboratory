import logging

from django.db import DatabaseError, connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from apps.events.models import Event
from apps.safety.services import current_risk_notice

PUBLIC_SITEMAP_URL_NAMES = ("home", "about", "beginners_safety", "members:list")

logger = logging.getLogger(__name__)


def home(request: HttpRequest) -> HttpResponse:
    events = Event.objects.public().upcoming().order_by("starts_at", "pk")[:3]
    return render(
        request,
        "core/home.html",
        {
            "upcoming_events": events,
            "registration_notice_available": current_risk_notice() is not None,
        },
    )


def about(request: HttpRequest) -> HttpResponse:
    return render(request, "core/about.html")


def beginners_safety(request: HttpRequest) -> HttpResponse:
    return render(request, "core/beginners_safety.html")


def sitemap(request: HttpRequest) -> HttpResponse:
    locations = [
        request.build_absolute_uri(reverse(url_name))
        for url_name in PUBLIC_SITEMAP_URL_NAMES
    ]
    return render(
        request,
        "core/sitemap.xml",
        {"locations": locations},
        content_type="application/xml",
    )


@require_GET
@never_cache
def health(request: HttpRequest) -> JsonResponse:
    """Report whether the app can reach its database, and nothing else."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        # The exception text can name hosts or users, so it is not logged.
        logger.error("Health check failed: the database is unavailable.")
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})


def permission_denied(request: HttpRequest, exception: Exception) -> HttpResponse:
    del exception
    return render(request, "core/errors/403.html", status=403)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    del exception
    return render(request, "core/errors/404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    return render(request, "core/errors/500.html", status=500)
