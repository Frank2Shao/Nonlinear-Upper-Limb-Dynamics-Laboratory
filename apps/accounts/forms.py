from allauth.account.forms import (
    ConfirmEmailVerificationCodeForm as AllauthConfirmEmailVerificationCodeForm,
)
from allauth.account.forms import (
    ConfirmLoginCodeForm as AllauthConfirmLoginCodeForm,
)
from allauth.account.forms import (
    RequestLoginCodeForm as AllauthRequestLoginCodeForm,
)
from allauth.account.forms import SignupForm as AllauthSignupForm
from allauth.account.models import EmailAddress
from django import forms

from .models import User, usu_id_validator
from .services import update_usu_identity


class OneTimeCodeInput(forms.TextInput):
    """Never echo a submitted authentication code back into HTML."""

    def format_value(self, value) -> None:
        return None


class NumericCodeFormMixin:
    """Give allauth code forms consistent mobile and paste-friendly input."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["code"].widget = OneTimeCodeInput(
            attrs={
                "autocomplete": "one-time-code",
                "autocapitalize": "off",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "spellcheck": "false",
            }
        )


class ConfirmEmailVerificationCodeForm(
    NumericCodeFormMixin,
    AllauthConfirmEmailVerificationCodeForm,
):
    pass


class ConfirmLoginCodeForm(
    NumericCodeFormMixin,
    AllauthConfirmLoginCodeForm,
):
    pass


class AccountIdentityForm(forms.Form):
    is_usyd_student = forms.BooleanField(
        label="Are you a USYD student?",
        required=False,
    )
    usu_id = forms.CharField(
        label="USU ID",
        max_length=64,
        required=False,
        validators=[usu_id_validator],
    )

    def __init__(self, *args, user: User, **kwargs) -> None:
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["is_usyd_student"].widget.attrs["x-model"] = "isUsyd"
        self.fields["usu_id"].widget.attrs["x-ref"] = "usuId"
        if not self.is_bound:
            self.initial.setdefault("is_usyd_student", user.is_usyd_student)
            self.initial.setdefault("usu_id", user.usu_id)

    def clean_usu_id(self) -> str | None:
        return User.normalize_usu_id(self.cleaned_data.get("usu_id"))

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        if (
            not cleaned_data.get("is_usyd_student")
            and cleaned_data.get("usu_id") is not None
        ):
            self.add_error(
                "usu_id",
                "USU ID is only available to USYD students.",
            )
        return cleaned_data

    def save(self) -> User:
        return update_usu_identity(
            user=self.user,
            is_usyd_student=bool(self.cleaned_data["is_usyd_student"]),
            usu_id=self.cleaned_data["usu_id"],
        )


class RequestLoginCodeForm(AllauthRequestLoginCodeForm):
    """Limit Magic Code login to an active account's verified email."""

    def clean_email(self) -> str:
        email = super().clean_email()
        user = getattr(self, "_user", None)
        if (
            user
            and not EmailAddress.objects.filter(
                user=user,
                email__iexact=email,
                verified=True,
            ).exists()
        ):
            self._user = None
        return email


class SignupForm(AllauthSignupForm):
    is_usyd_student = forms.BooleanField(
        label="Are you a USYD student?",
        required=False,
    )
    usu_id = forms.CharField(
        label="USU ID",
        max_length=64,
        required=False,
        validators=[usu_id_validator],
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["is_usyd_student"].widget.attrs["x-model"] = "isUsyd"
        self.fields["usu_id"].widget.attrs["x-ref"] = "usuId"
        self.order_fields(
            (
                "username",
                "email",
                "password1",
                "password2",
                "is_usyd_student",
                "usu_id",
            )
        )

    def clean_usu_id(self) -> str | None:
        return User.normalize_usu_id(self.cleaned_data.get("usu_id"))

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        if (
            not cleaned_data.get("is_usyd_student")
            and cleaned_data.get("usu_id") is not None
        ):
            self.add_error(
                "usu_id",
                "USU ID is only available to USYD students.",
            )
        return cleaned_data

    def save(self, request) -> User:
        user = super().save(request)
        update_usu_identity(
            user=user,
            is_usyd_student=bool(self.cleaned_data["is_usyd_student"]),
            usu_id=self.cleaned_data["usu_id"],
        )
        user.refresh_from_db(
            fields=(
                "is_usyd_student",
                "usu_id",
                "usu_review_status",
                "usu_reviewed_at",
                "usu_reviewed_by",
            )
        )
        return user
