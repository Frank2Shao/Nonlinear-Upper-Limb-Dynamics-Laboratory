from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse

PUBLIC_SITEMAP_URL_NAMES = ("home", "about", "beginners_safety", "members:list")


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "core/home.html")


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


def permission_denied(request: HttpRequest, exception: Exception) -> HttpResponse:
    del exception
    return render(request, "core/errors/403.html", status=403)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    del exception
    return render(request, "core/errors/404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    return render(request, "core/errors/500.html", status=500)
