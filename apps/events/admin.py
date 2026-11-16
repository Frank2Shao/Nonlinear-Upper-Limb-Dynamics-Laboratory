"""Django Admin configuration for club events."""

from typing import ClassVar

from django import forms
from django.contrib import admin

from .models import Event, EventRegistration


class EventAdminForm(forms.ModelForm):
    map_url = forms.URLField(required=False, assume_scheme="https")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = (
        "title",
        "starts_at",
        "ends_at",
        "is_published",
        "registration_open",
    )
    list_filter = ("is_published", "registration_open")
    search_fields = ("title", "description", "venue_text")
    prepopulated_fields: ClassVar[dict[str, tuple[str, ...]]] = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "starts_at"


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "member_name",
        "member_username",
        "member_email",
        "member_usu_id",
        "status",
        "risk_notice_version",
        "registered_at",
        "cancelled_at",
    )
    list_filter = ("event", "status", "risk_notice")
    search_fields = (
        "event__title",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__usu_id",
        "risk_notice__version",
    )
    list_select_related = ("event", "user", "risk_notice")
    date_hierarchy = "registered_at"
    actions: ClassVar[tuple] = ()
    fields = (
        "event",
        "member_name",
        "member_username",
        "member_email",
        "member_usu_id",
        "status",
        "risk_notice_version",
        "registered_at",
        "risk_notice_accepted_at",
        "cancelled_at",
    )
    readonly_fields = fields

    @admin.display(description="Member name", ordering="user__username")
    def member_name(self, registration: EventRegistration) -> str:
        return registration.user.get_full_name() or registration.user.username

    @admin.display(description="Username", ordering="user__username")
    def member_username(self, registration: EventRegistration) -> str:
        return registration.user.username

    @admin.display(description="Email", ordering="user__email")
    def member_email(self, registration: EventRegistration) -> str:
        return registration.user.email

    @admin.display(description="USU ID", ordering="user__usu_id")
    def member_usu_id(self, registration: EventRegistration) -> str:
        return registration.user.usu_id or "Not provided"

    @admin.display(description="Risk Notice version", ordering="risk_notice__version")
    def risk_notice_version(self, registration: EventRegistration) -> str:
        return registration.risk_notice.version

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
