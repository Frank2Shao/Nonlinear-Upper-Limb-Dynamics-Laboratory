"""Risk notice version activation for non-production environments."""

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from .models import RiskNoticeVersion


def current_risk_notice():
    if not settings.RISK_NOTICE_DRAFT_VISIBLE:
        return None
    return RiskNoticeVersion.objects.filter(is_current=True).first()


@transaction.atomic
def activate_risk_notice(version_id: int) -> None:
    if not settings.RISK_NOTICE_DRAFT_VISIBLE:
        raise PermissionDenied

    # Lock all existing versions in a consistent order, including when none is current.
    versions = list(RiskNoticeVersion.objects.select_for_update().order_by("pk"))
    target = next((version for version in versions if version.pk == version_id), None)
    if target is None:
        raise RiskNoticeVersion.DoesNotExist
    if target.is_current:
        return

    RiskNoticeVersion.objects.filter(is_current=True).update(is_current=False)
    RiskNoticeVersion.objects.filter(pk=target.pk).update(
        is_current=True, activated_at=timezone.now()
    )
