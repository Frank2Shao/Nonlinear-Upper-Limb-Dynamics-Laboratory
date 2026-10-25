from django import forms

from .models import MemberProfile


class MemberProfileForm(forms.ModelForm):
    other_social_url = forms.URLField(required=False, assume_scheme="https")

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
            "is_published",
        )
