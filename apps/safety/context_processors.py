"""Template context for environment-gated safety content."""

from django.conf import settings
from django.http import HttpRequest


def risk_notice_visibility(request: HttpRequest) -> dict[str, bool]:
    """Expose only the configured draft visibility state to templates."""
    return {"draft_risk_notice_visible": settings.RISK_NOTICE_DRAFT_VISIBLE}
