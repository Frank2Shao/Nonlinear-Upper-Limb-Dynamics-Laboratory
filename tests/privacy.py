"""Shared assertion for public-page privacy boundaries.

Each test still names the exact private values it protects; this helper only
standardises the check and reports every leaked value at once.
"""

from collections.abc import Iterable


def private_identity_values(user) -> tuple[str, ...]:
    """Email, USU ID and USU review status: never shown on public pages."""
    values = [user.email]
    if user.usu_id:
        values += [user.usu_id, user.get_usu_review_status_display()]
    return tuple(values)


def assert_no_private_values(
    content: str,
    private_values: Iterable[object],
    *,
    context: str = "Response",
) -> None:
    values = [str(value) for value in private_values]
    assert all(values), f"{context}: private values must be non-empty: {values!r}"
    leaked = [value for value in values if value in content]
    assert leaked == [], f"{context} exposes private values: {leaked!r}"
