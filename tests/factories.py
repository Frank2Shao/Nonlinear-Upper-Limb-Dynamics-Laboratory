"""Synthetic account and profile builders shared by the test suite.

All values are fictitious. Tests that care about a specific email domain,
password or field value pass it explicitly so the behaviour under test stays
visible at the call site.
"""

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from apps.members.models import MemberProfile

DEFAULT_PASSWORD = "test-password"


def create_user(
    username: str,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD,
    verified: bool | None = None,
    can_review_usu_id: bool = False,
    **user_fields,
):
    """Create a synthetic user.

    ``verified`` controls the allauth EmailAddress row: ``None`` creates no row,
    ``True`` or ``False`` creates a primary row with that verification state.
    """
    email = email if email is not None else f"{username}@example.com"
    user = get_user_model().objects.create_user(
        username=username,
        email=email,
        password=password,
        **user_fields,
    )
    if verified is not None:
        EmailAddress.objects.create(
            user=user,
            email=email,
            primary=True,
            verified=verified,
        )
    if can_review_usu_id:
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="accounts",
                codename="review_usu_id",
            )
        )
    return user


def create_member(
    username: str,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD,
    verified: bool | None = True,
    user_fields: dict | None = None,
    **profile_fields,
) -> tuple:
    """Create a user with a primary EmailAddress and a MemberProfile."""
    user = create_user(
        username,
        email=email,
        password=password,
        verified=verified,
        **(user_fields or {}),
    )
    return user, MemberProfile.objects.create(user=user, **profile_fields)
