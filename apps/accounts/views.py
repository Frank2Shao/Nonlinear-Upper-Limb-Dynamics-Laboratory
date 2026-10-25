from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import AccountIdentityForm


@login_required
def account(request: HttpRequest) -> HttpResponse:
    form = AccountIdentityForm(
        request.POST if request.method == "POST" else None,
        user=request.user,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your account information has been updated.")
        return redirect("account")

    email_is_verified = EmailAddress.objects.filter(
        user=request.user,
        email__iexact=request.user.email,
        verified=True,
    ).exists()
    return render(
        request,
        "accounts/account.html",
        {
            "form": form,
            "email_is_verified": email_is_verified,
        },
    )
