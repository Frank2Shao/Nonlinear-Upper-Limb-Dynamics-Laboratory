from typing import ClassVar

from django import forms
from django.core.exceptions import ValidationError

from .models import MemberProfile


class MemberProfileForm(forms.ModelForm):
    other_social_url = forms.URLField(required=False, assume_scheme="https")
    remove_avatar = forms.BooleanField(
        required=False,
        label="Remove current avatar",
    )

    class Meta:
        model = MemberProfile
        fields = (
            "display_name",
            "avatar",
            "bio",
            "experience_level",
            "preferred_arm",
            "instagram_handle",
            "other_social_url",
        )
        widgets: ClassVar[dict[str, forms.Widget]] = {"avatar": forms.FileInput()}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["avatar"].widget.attrs["aria-describedby"] = "avatar-privacy-help"

    def clean(self):
        cleaned_data = super().clean()
        if self.files.get("avatar") and cleaned_data.get("remove_avatar"):
            self.add_error(
                "remove_avatar",
                "Choose a new avatar or remove the current avatar, not both.",
            )
        return cleaned_data

    def clean_display_name(self) -> str | None:
        value = (self.cleaned_data.get("display_name") or "").strip()
        if not value:
            return None

        duplicate_names = MemberProfile.objects.filter(display_name__iexact=value)
        if self.instance.pk:
            duplicate_names = duplicate_names.exclude(pk=self.instance.pk)
        if duplicate_names.exists():
            raise ValidationError("This display name is already in use.")
        return value

    def clean_instagram_handle(self) -> str:
        value = self.cleaned_data.get("instagram_handle") or ""
        return value.removeprefix("@").strip()
