"""Production logs and error emails that cannot carry member data.

They are built from an allow list: exception types, file:line, route name and
status code. Messages, arguments, URLs, headers, users and IPs are never read.
"""

import logging
import time
from pathlib import PurePath

from django.core.mail import mail_admins

REPEAT_AFTER_SECONDS = 60 * 60

logger = logging.getLogger(__name__)


def safe_summary(record: logging.LogRecord) -> list[str]:
    heading = [record.levelname, record.name]
    status = getattr(record, "status_code", None)
    if status:
        match = getattr(getattr(record, "request", None), "resolver_match", None)
        heading += [f"status={status}", f"route={match.view_name if match else '-'}"]
    elif record.name.startswith("apps.") or (
        record.name == "gunicorn.error"
        and (record.levelno == logging.INFO or record.args)
    ):
        # Fixed text, without its arguments. gunicorn's only messages with data
        # already inside them are warnings and errors that have no arguments.
        heading.append(str(record.msg))
    else:
        heading.append(f"at {record.module}:{record.lineno}")
    lines = [" ".join(heading)]

    error = record.exc_info[1] if record.exc_info else None
    seen = set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        lines.append(f"  {type(error).__name__}")
        trace = error.__traceback__
        while trace is not None:
            file = "/".join(PurePath(trace.tb_frame.f_code.co_filename).parts[-3:])
            lines.append(f"    {file}:{trace.tb_lineno}")
            trace = trace.tb_next
        error = error.__cause__ or (
            None if error.__suppress_context__ else error.__context__
        )
    return lines


class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        summary = "\n".join(safe_summary(record))
        return f"{self.formatTime(record)} {summary}"


class SafeAdminEmailHandler(logging.Handler):
    """Email the same summary, at most once an hour per error in each process."""

    def __init__(self) -> None:
        super().__init__()
        self.last_sent: dict[str, float] = {}

    def emit(self, record: logging.LogRecord) -> None:
        try:
            body = "\n".join(safe_summary(record))
            now = time.monotonic()
            sent = self.last_sent.get(body)
            if sent is not None and now - sent < REPEAT_AFTER_SECONDS:
                return
            self.last_sent[body] = now
            mail_admins("Server error", body, fail_silently=False)
        except Exception:
            # Not handleError(): it would print the original message and arguments.
            logger.warning("A server error email could not be sent.", exc_info=True)
