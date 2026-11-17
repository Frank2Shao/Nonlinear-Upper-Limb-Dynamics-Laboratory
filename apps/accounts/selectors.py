"""Read-only account eligibility checks shared by member-facing apps."""

from allauth.account.models import EmailAddress


def is_verified_active_member(user) -> bool:
    """Return whether the user is an active account with a verified email."""
    return bool(
        user.is_authenticated
        and user.is_active
        and EmailAddress.objects.filter(user=user, verified=True).exists()
    )
