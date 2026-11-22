"""Server error reports that never carry member, form or session data."""

import re

from django.views.debug import SafeExceptionReporterFilter


class PrivateExceptionReporterFilter(SafeExceptionReporterFilter):
    """Keep the traceback, redact the values around it.

    Error reports reach administrators by email, so they must not contain
    passwords, one-time codes, Email addresses, USU IDs, other form values,
    local variables, or session and CSRF cookies. Like Django's own filter, it
    only redacts when active (DEBUG off), so local debug pages stay useful.
    """

    hidden_settings = re.compile(
        "API|AUTH|TOKEN|KEY|SECRET|PASS|SIGNATURE|COOKIE|SESSION|CSRF"
        "|EMAIL|DATABASE|ADMINS",
        flags=re.IGNORECASE,
    )

    def get_post_parameters(self, request):
        if request is None:
            return {}
        if not self.is_active(request):
            return super().get_post_parameters(request)
        cleansed = request.POST.copy()
        for key in cleansed:
            cleansed[key] = self.cleansed_substitute
        return cleansed

    def get_safe_cookies(self, request):
        if not self.is_active(request):
            return super().get_safe_cookies(request)
        return {name: self.cleansed_substitute for name in request.COOKIES}

    def get_traceback_frame_variables(self, request, tb_frame):
        if not self.is_active(request):
            return super().get_traceback_frame_variables(request, tb_frame)
        return [(name, self.cleansed_substitute) for name in tb_frame.f_locals]
