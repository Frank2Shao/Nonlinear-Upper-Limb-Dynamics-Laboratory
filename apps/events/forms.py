from django import forms


class EventRegistrationForm(forms.Form):
    risk_notice_id = forms.IntegerField(widget=forms.HiddenInput)
    accepted = forms.BooleanField()


class EventCancellationForm(forms.Form):
    confirmed = forms.BooleanField()
