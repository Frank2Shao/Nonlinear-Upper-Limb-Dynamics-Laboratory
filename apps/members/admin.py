from django.contrib import admin

from .models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "display_name",
        "researcher_number",
        "is_published",
        "is_hidden_by_admin",
        "updated_at",
    )
    list_filter = ("is_published", "is_hidden_by_admin", "experience_level")
    search_fields = ("user__username", "user__email", "display_name")
    readonly_fields = (
        "user",
        "display_name",
        "avatar",
        "bio",
        "experience_level",
        "preferred_arm",
        "instagram_handle",
        "other_social_url",
        "is_published",
        "created_at",
        "updated_at",
    )
    fields = (
        "user",
        "display_name",
        "avatar",
        "bio",
        "experience_level",
        "preferred_arm",
        "instagram_handle",
        "other_social_url",
        "is_published",
        "is_hidden_by_admin",
        "executive_role",
        "researcher_number",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
