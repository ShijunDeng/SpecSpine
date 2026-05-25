from __future__ import annotations

import re

__all__ = [
    "AC_ID_RE",
    "CHECKBOX_TASK_RE",
    "DEP_PATTERN",
    "TASK_DEP_PATTERN",
]

CHECKBOX_TASK_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
AC_ID_RE = re.compile(r"\bAC\d{3,}\b", re.IGNORECASE)
DEP_PATTERN = re.compile(
    r"(?:depends\s+on|after|blocked\s+by|requires|prerequisite:\s*)"
    r"([a-z0-9]+(?:-[a-z0-9]+)*)",
    re.IGNORECASE,
)
TASK_DEP_PATTERN = re.compile(
    r"(?:after|depends\s+on|blocked\s+by)\s+([Tt]\d{3,})",
    re.IGNORECASE,
)
