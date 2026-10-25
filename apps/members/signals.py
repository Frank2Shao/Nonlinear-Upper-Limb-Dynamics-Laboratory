from allauth.account.signals import email_confirmed
from django.dispatch import receiver

from .services import ensure_member_profile


@receiver(email_confirmed, dispatch_uid="members.ensure_profile_after_email_confirmed")
def ensure_profile_after_email_confirmed(sender, email_address, **kwargs) -> None:
    ensure_member_profile(user=email_address.user)
