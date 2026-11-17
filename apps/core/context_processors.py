"""Template context for the shared site header."""

from django.http import HttpRequest

# Each primary-navigation link is marked aria-current="page" when the
# resolved view belongs to its section.
NAV_SECTION_BY_VIEW_NAME = {
    "home": "home",
    "about": "about",
    "beginners_safety": "beginners_safety",
    "members:list": "members",
    "members:detail": "members",
    "safety:risk_notice": "risk_notice",
    "account": "account",
    "account_change_password": "account",
    "account_login": "login",
    "account_request_login_code": "login",
    "account_confirm_login_code": "login",
    "account_signup": "signup",
    "account_email_verification_sent": "signup",
}
NAV_SECTION_BY_NAMESPACE = {"events": "events"}


def navigation_section(request: HttpRequest) -> dict[str, str | None]:
    """Expose the header section for the current request, if any."""
    match = request.resolver_match
    if match is None:
        return {"nav_section": None}
    section = NAV_SECTION_BY_VIEW_NAME.get(match.view_name)
    if section is None:
        section = NAV_SECTION_BY_NAMESPACE.get(match.namespace)
    return {"nav_section": section}
