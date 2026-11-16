"""Root URL configuration for the NULDL website."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path


def development_media_urlpatterns() -> list[URLPattern | URLResolver]:
    if not settings.DEBUG:
        return []
    return static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("", include("apps.safety.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.members.urls")),
    path("events/", include("apps.events.urls")),
    path("accounts/", include("allauth.urls")),
]

urlpatterns += development_media_urlpatterns()

handler403 = "apps.core.views.permission_denied"
handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
