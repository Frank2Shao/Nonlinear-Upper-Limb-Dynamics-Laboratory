"""Deployment checks for settings that only matter in Production."""

from django.conf import settings
from django.core.checks import Tags, Warning, register


@register(Tags.security, deploy=True)
def server_error_recipients(app_configs, **kwargs):
    """Warn when server errors would not be emailed to anyone."""
    if settings.ADMINS:
        return []
    return [
        Warning(
            "ADMINS is empty, so server errors will not be emailed.",
            hint="Set DJANGO_ADMINS to one or more administrator addresses.",
            id="core.W001",
        )
    ]
