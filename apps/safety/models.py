"""Versioned risk notice content."""

from typing import ClassVar

from django.db import models


class RiskNoticeVersion(models.Model):
    version = models.CharField(max_length=64, unique=True)
    body = models.TextField()
    is_current = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, editable=False)

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["is_current"],
                condition=models.Q(is_current=True),
                name="safety_one_current_risk_notice",
            ),
        ]

    def __str__(self) -> str:
        return self.version
