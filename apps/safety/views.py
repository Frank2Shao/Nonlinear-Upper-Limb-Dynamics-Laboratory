"""Environment-gated safety content views."""

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render


def risk_notice(request: HttpRequest) -> HttpResponse:
    """Render the draft only when the active environment explicitly allows it."""
    if not settings.RISK_NOTICE_DRAFT_VISIBLE:
        raise Http404
    return render(request, "safety/risk_notice.html")
