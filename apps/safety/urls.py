"""Public URL routes owned by the safety application."""

from django.urls import path

from .views import risk_notice

app_name = "safety"

urlpatterns = [
    path("risk-notice/", risk_notice, name="risk_notice"),
]
