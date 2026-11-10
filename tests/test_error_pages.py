import pytest
from django.test import override_settings
from django.urls import reverse

ERROR_CASES = (
    ("/test-error/403/", 403, "core/errors/403.html", "Access Denied"),
    ("/test-error/missing/", 404, "core/errors/404.html", "Page Not Found"),
    ("/test-error/500/", 500, "core/errors/500.html", "Something Went Wrong"),
)


@override_settings(DEBUG=False, ROOT_URLCONF="tests.error_urls")
@pytest.mark.parametrize(("path", "status", "template_name", "heading"), ERROR_CASES)
def test_real_error_handlers_use_safe_shared_pages(
    client, path, status, template_name, heading
):
    client.raise_request_exception = False

    response = client.get(path)

    assert response.status_code == status
    assert template_name in [template.name for template in response.templates]
    content = response.content.decode()
    assert f"<title>{heading} | NULDL Armwrestling Club</title>" in content
    assert content.count("<h1") == 1
    assert f"<h1>{heading}</h1>" in content
    assert f'href="{reverse("home")}">Return Home</a>' in content
    assert 'href="/static/css/site.css"' in content
    assert '<header class="site-header">' in content
    assert '<footer class="site-footer">' in content

    content_lower = content.lower()
    for forbidden_text in (
        "traceback",
        "runtimeerror",
        "synthetic server failure",
        "django_secret_key",
        "e:\\frank",
        "contact us",
        "email us",
    ):
        assert forbidden_text not in content_lower


def test_project_urlconf_registers_all_error_handlers():
    import config.urls

    assert config.urls.handler403 == "apps.core.views.permission_denied"
    assert config.urls.handler404 == "apps.core.views.page_not_found"
    assert config.urls.handler500 == "apps.core.views.server_error"
