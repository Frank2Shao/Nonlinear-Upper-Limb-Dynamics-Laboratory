"""Template helpers for the project's form field markup."""

from django import template
from django.forms import BoundField
from django.utils.safestring import SafeString

register = template.Library()


@register.filter
def plain_label(field: BoundField) -> SafeString:
    """Render the field's label (or legend) without Django's trailing colon.

    design_document.md 7.11 drops the default label suffix on the site's own
    forms. Django Admin renders its labels separately and keeps its suffix.
    """
    if field.use_fieldset:
        return field.legend_tag(label_suffix="")
    return field.label_tag(label_suffix="")
