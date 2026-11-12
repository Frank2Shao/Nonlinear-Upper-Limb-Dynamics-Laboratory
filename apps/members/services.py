from django.db import transaction

from .models import MemberProfile


@transaction.atomic
def ensure_member_profile(*, user) -> tuple[MemberProfile, bool]:
    return MemberProfile.objects.get_or_create(user=user)


def save_member_profile_form(*, form) -> MemberProfile:
    """Save an edited profile and clean up replaced or failed avatar files."""
    profile = form.instance
    avatar_field = MemberProfile._meta.get_field("avatar")
    storage = avatar_field.storage
    previous_avatar_name = (
        MemberProfile.objects.only("avatar").get(pk=profile.pk).avatar.name or None
    )

    profile = form.save(commit=False)
    if form.cleaned_data.get("remove_avatar"):
        profile.avatar = None

    try:
        with transaction.atomic():
            profile.save()
            form.save_m2m()
    except Exception:
        failed_avatar = profile.avatar
        failed_avatar_name = failed_avatar.name or None
        if (
            failed_avatar_name
            and failed_avatar_name != previous_avatar_name
            and getattr(failed_avatar, "_committed", False)
        ):
            storage.delete(failed_avatar_name)
        raise

    current_avatar_name = profile.avatar.name or None
    if previous_avatar_name and previous_avatar_name != current_avatar_name:
        storage.delete(previous_avatar_name)

    return profile


@transaction.atomic
def set_profile_publication(*, user, is_published: bool) -> MemberProfile:
    """Set the current member's publication preference idempotently."""
    profile = MemberProfile.objects.select_for_update().get(user=user)
    if profile.is_published == is_published:
        return profile

    profile.is_published = is_published
    profile.save(update_fields=["is_published", "updated_at"])
    return profile
