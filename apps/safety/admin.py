"""Admin workflow for synthetic risk notice versions."""

from typing import ClassVar

from django import forms
from django.conf import settings
from django.contrib import admin, messages

from .models import RiskNoticeVersion
from .services import activate_risk_notice


class RiskNoticeVersionForm(forms.ModelForm):
    def clean_body(self):
        body = self.cleaned_data["body"]
        lines = body.splitlines()
        if len(lines) < 2 or lines[0] != "SYNTHETIC TEST ONLY":
            raise forms.ValidationError(
                "Start the body with SYNTHETIC TEST ONLY on its own line."
            )
        return body


@admin.register(RiskNoticeVersion)
class RiskNoticeVersionAdmin(admin.ModelAdmin):
    form = RiskNoticeVersionForm
    list_display = ("version", "is_current", "created_at", "activated_at")
    actions: ClassVar[list[str]] = ["make_current"]

    def has_module_permission(self, request):
        return settings.RISK_NOTICE_DRAFT_VISIBLE and super().has_module_permission(
            request
        )

    def has_view_permission(self, request, obj=None):
        return settings.RISK_NOTICE_DRAFT_VISIBLE and super().has_view_permission(
            request, obj
        )

    def has_add_permission(self, request):
        return settings.RISK_NOTICE_DRAFT_VISIBLE and super().has_add_permission(
            request
        )

    def has_change_permission(self, request, obj=None):
        return settings.RISK_NOTICE_DRAFT_VISIBLE and super().has_change_permission(
            request, obj
        )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        metadata = ("is_current", "created_at", "activated_at")
        return (*metadata, "version", "body") if obj else metadata

    def save_model(self, request, obj, form, change):
        if not change:
            super().save_model(request, obj, form, change)

    @admin.action(
        permissions=["change"], description="Make selected test version current"
    )
    def make_current(self, request, queryset):
        selected = list(queryset[:2])
        if len(selected) != 1:
            self.message_user(request, "Select exactly one version.", messages.ERROR)
            return
        version = selected[0]
        activate_risk_notice(version.pk)
        self.log_change(request, version, "Made synthetic Risk Notice version current.")
        self.message_user(request, "Current test version updated.", messages.SUCCESS)
