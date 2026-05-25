from __future__ import annotations

import re

AC_ID_RE = re.compile(r"AC\d{3}")
TASK_ID_RE = re.compile(r"(?:TASK|T)\d{3}")
COV_LINK_DONE_RE = re.compile(r"-\s*\[\s*[xX]\s*\]\s+AC\d{3}\s*->")
COV_LINK_TOTAL_RE = re.compile(r"-\s*\[\s*[ xX]\s*\]\s+AC\d{3}\s*->")


__all__ = [
    "AC_ID_RE",
    "TASK_ID_RE",
    "COV_LINK_DONE_RE",
    "COV_LINK_TOTAL_RE",
]
