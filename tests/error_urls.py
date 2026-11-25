"""Isolated URL configuration for exercising Django error handlers."""

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.urls import path

from config.urls import urlpatterns as project_urlpatterns


def forbidden_view(_request: HttpRequest) -> HttpResponse:
    raise PermissionDenied


def server_failure_view(_request: HttpRequest) -> HttpResponse:
    raise RuntimeError("Synthetic server failure")


def private_failure_view(request: HttpRequest, token: str) -> HttpResponse:
    try:
        raise ValueError(f"CHAINED-PRIVATE {token}")
    except ValueError as error:
        raise RuntimeError(f"MESSAGE-PRIVATE {request.GET.get('email')}") from error


urlpatterns = [
    *project_urlpatterns,
    path("test-error/403/", forbidden_view),
    path("test-error/500/", server_failure_view),
    path(
        "test-error/private/<token>/",
        private_failure_view,
        name="test_private_failure",
    ),
]

handler403 = "apps.core.views.permission_denied"
handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
