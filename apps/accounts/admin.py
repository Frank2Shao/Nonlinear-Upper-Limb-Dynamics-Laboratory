from collections.abc import Callable

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import User
from .services import review_usu_id


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "username",
        "email",
        "is_usyd_student",
        "usu_id",
        "usu_review_status",
        "is_active",
    )
    list_filter = (
        "usu_review_status",
        "is_usyd_student",
        "is_active",
    )
    search_fields = ("username", "email", "usu_id")
    ordering = ("username",)
    actions = ("verify_usu_ids", "reject_usu_ids")

    usu_identity_fields = (
        "is_usyd_student",
        "usu_id",
        "usu_review_status",
        "usu_reviewed_at",
        "usu_reviewed_by",
    )
    reviewer_fieldsets = (
        (
            "Account",
            {
                "fields": (
                    "username",
                    "email",
                    "is_active",
                )
            },
        ),
        ("USU identity", {"fields": usu_identity_fields}),
    )

    def get_fieldsets(self, request: HttpRequest, obj=None):
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj) + (
                ("USU identity", {"fields": self.usu_identity_fields}),
            )
        return self.reviewer_fieldsets

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if request.user.is_superuser:
            return self.usu_identity_fields
        return tuple(
            field
            for fieldset in self.reviewer_fieldsets
            for field in fieldset[1]["fields"]
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(is_usyd_student=True, usu_id__isnull=False)

    def has_module_permission(self, request: HttpRequest) -> bool:
        return self.has_review_usu_id_permission(request)

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return self.has_review_usu_id_permission(request)

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return self.has_review_usu_id_permission(request)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.is_active and request.user.is_superuser

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_active and request.user.is_superuser

    def has_review_usu_id_permission(self, request: HttpRequest) -> bool:
        return (
            request.user.is_active
            and request.user.is_staff
            and request.user.has_perm("accounts.review_usu_id")
        )

    def render_change_form(
        self,
        request: HttpRequest,
        context: dict[str, object],
        *args,
        **kwargs,
    ):
        if not request.user.is_superuser:
            context.update(
                show_save=False,
                show_save_and_continue=False,
                show_save_and_add_another=False,
                show_delete=False,
            )
        return super().render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change) -> None:
        if not request.user.is_superuser:
            raise PermissionDenied("USU reviewers cannot edit User records directly.")
        super().save_model(request, obj, form, change)

    @admin.action(
        description="Mark selected USU IDs as verified",
        permissions=("review_usu_id",),
    )
    def verify_usu_ids(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        self._review_selected(
            request,
            queryset,
            status=User.UsuReviewStatus.VERIFIED,
        )

    @admin.action(
        description="Mark selected USU IDs as rejected",
        permissions=("review_usu_id",),
    )
    def reject_usu_ids(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        self._review_selected(
            request,
            queryset,
            status=User.UsuReviewStatus.REJECTED,
        )

    def _review_selected(
        self,
        request: HttpRequest,
        queryset: QuerySet[User],
        *,
        status: str,
    ) -> None:
        reviewed_count = 0
        skipped_count = 0
        review: Callable[..., User] = review_usu_id
        for user in queryset:
            try:
                review(user=user, reviewer=request.user, status=status)
            except (PermissionDenied, ValidationError):
                skipped_count += 1
            else:
                reviewed_count += 1

        if reviewed_count:
            self.message_user(
                request,
                f"Reviewed {reviewed_count} USU ID submission(s).",
                level=messages.SUCCESS,
            )
        if skipped_count:
            self.message_user(
                request,
                f"Skipped {skipped_count} invalid USU ID submission(s).",
                level=messages.WARNING,
            )
