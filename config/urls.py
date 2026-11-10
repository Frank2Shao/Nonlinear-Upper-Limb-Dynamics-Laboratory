"""Root URL configuration for the NULDL website."""

from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("", include("apps.safety.urls")),
    path("", include("apps.accounts.urls")),
    path("accounts/", include("allauth.urls")),
]

handler403 = "apps.core.views.permission_denied"
handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
