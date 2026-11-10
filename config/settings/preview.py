"""Private preview settings with an explicit draft-content gate."""

from .production import *

RISK_NOTICE_DRAFT_VISIBLE = required_bool_env("RISK_NOTICE_DRAFT_VISIBLE")
