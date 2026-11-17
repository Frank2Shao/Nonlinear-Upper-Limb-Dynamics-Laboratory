"""Field validators and normalizers shared by project models."""

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

HTTPS_PREFIX = "https://"


def validate_https_url(value: str) -> None:
    """Accept only well-formed HTTPS URLs; empty values are left to the field."""
    if not value:
        return
    if not value.lower().startswith(HTTPS_PREFIX):
        raise ValidationError("Use an HTTPS URL.")
    URLValidator(schemes=["https"])(value)


def normalize_https_scheme(value: str) -> str:
    """Lowercase an HTTPS scheme so database constraints see ``https://``."""
    if value.lower().startswith(HTTPS_PREFIX):
        return f"{HTTPS_PREFIX}{value[len(HTTPS_PREFIX) :]}"
    return value
