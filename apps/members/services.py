from django.db import transaction

from .models import MemberProfile


@transaction.atomic
def ensure_member_profile(*, user) -> tuple[MemberProfile, bool]:
    return MemberProfile.objects.get_or_create(user=user)
