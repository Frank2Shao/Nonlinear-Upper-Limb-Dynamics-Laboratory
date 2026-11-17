from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models.functions import Coalesce, Lower
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from apps.accounts.selectors import is_verified_active_member

from .forms import MemberProfileForm
from .models import MemberProfile
from .services import save_member_profile_form, set_profile_publication


@require_GET
def member_list(request: HttpRequest) -> HttpResponse:
    profiles = (
        MemberProfile.objects.public()
        .select_related("user")
        .annotate(
            public_sort_name=Lower(Coalesce("display_name", "user__username")),
        )
        .order_by(
            "public_sort_name",
            Lower("user__username"),
            "user__username",
            "pk",
        )
    )
    return render(
        request,
        "members/member_list.html",
        {"profiles": profiles},
    )


@require_GET
def member_detail(request: HttpRequest, username: str) -> HttpResponse:
    profile = get_object_or_404(
        MemberProfile.objects.public().select_related("user"),
        user__username=username,
    )
    return render(
        request,
        "members/member_detail.html",
        {"profile": profile},
    )


def _get_owned_profile(request: HttpRequest) -> MemberProfile:
    if not is_verified_active_member(request.user):
        raise PermissionDenied

    return get_object_or_404(
        MemberProfile.objects.select_related("user"),
        user=request.user,
    )


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    profile = _get_owned_profile(request)
    form = MemberProfileForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=profile,
    )

    if request.method == "POST" and form.is_valid():
        save_member_profile_form(form=form)
        messages.success(request, "Your profile has been updated.")
        return redirect("account")

    return render(
        request,
        "members/profile_edit.html",
        {"form": form, "profile": profile},
    )


@login_required
@require_GET
def profile_preview(request: HttpRequest) -> HttpResponse:
    profile = _get_owned_profile(request)
    return render(
        request,
        "members/profile_preview.html",
        {"profile": profile},
    )


@login_required
@require_http_methods(["GET", "POST"])
def profile_publish(request: HttpRequest) -> HttpResponse:
    profile = _get_owned_profile(request)
    if request.method == "POST":
        set_profile_publication(user=request.user, is_published=True)
        messages.success(request, "Your profile publication preference has been saved.")
        return redirect("members:profile_preview")

    return render(
        request,
        "members/profile_publish_confirm.html",
        {
            "profile": profile,
            "public_profile_path": reverse(
                "members:detail",
                kwargs={"username": request.user.get_username()},
            ),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def profile_unpublish(request: HttpRequest) -> HttpResponse:
    profile = _get_owned_profile(request)
    if request.method == "POST":
        set_profile_publication(user=request.user, is_published=False)
        messages.success(request, "Your profile is no longer published.")
        return redirect("members:profile_preview")

    return render(
        request,
        "members/profile_unpublish_confirm.html",
        {"profile": profile},
    )
