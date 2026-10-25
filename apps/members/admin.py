from django.contrib import admin

from .models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "display_name",
        "is_published",
        "is_hidden_by_admin",
        "updated_at",
    )
    list_filter = ("is_published", "is_hidden_by_admin", "experience_level")
    search_fields = ("user__username", "user__email", "display_name")
    readonly_fields = ("created_at", "updated_at")
