from __future__ import annotations

import re

__all__ = [
    "AC_ID_RE",
    "COV_LINK_RE",
    "FEATURE_ID_RE",
    "GIT_LOG_DATE_RE",
    "LIFECYCLE_STATUS_RE",
    "QUALITY_CHECK_RE",
    "TASK_ID_RE",
]

GIT_LOG_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
LIFECYCLE_STATUS_RE = re.compile(r"Status:\s*(\S+)", re.IGNORECASE)
FEATURE_ID_RE = re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")
QUALITY_CHECK_RE = re.compile(r"(QC\d{3})")
COV_LINK_RE = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")
