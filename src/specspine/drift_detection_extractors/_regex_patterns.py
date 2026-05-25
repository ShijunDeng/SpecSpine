from __future__ import annotations

import re

__all__ = [
    "AC_ID_RE",
    "TASK_ID_RE",
    "QUALITY_CHECK_RE",
    "COV_LINK_RE",
]

AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")
QUALITY_CHECK_RE = re.compile(r"(QC\d{3})")
COV_LINK_RE = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")
