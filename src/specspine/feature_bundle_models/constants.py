from __future__ import annotations

import re
from pathlib import Path

__all__ = [
    "FEATURE_SLUG_RE",
    "FEATURE_FILE_PATHS",
    "FEATURE_STATUSES",
    "FEATURE_PRIORITIES",
    "FEATURE_TRANSITIONS",
    "FEATURE_DIRECTORIES",
    "CHECKBOX_TASK_RE",
    "AC_ID_RE",
]

FEATURE_SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
FEATURE_FILE_PATHS = {
    "spec": "specs/features/{slug}.md",
    "execution": "execution/features/{slug}.md",
    "quality": "quality/features/{slug}.md",
}
FEATURE_STATUSES = (
    "proposed",
    "planned",
    "in-progress",
    "implemented",
    "validated",
    "archived",
)
FEATURE_PRIORITIES = ("high", "medium", "low")
FEATURE_TRANSITIONS = {
    "proposed": ("planned", "archived"),
    "planned": ("in-progress", "archived"),
    "in-progress": ("implemented", "planned", "archived"),
    "implemented": ("validated", "in-progress", "archived"),
    "validated": ("archived", "implemented"),
    "archived": (),
}
FEATURE_DIRECTORIES = {
    kind: str(Path(pattern.format(slug="__feature__")).parent)
    for kind, pattern in FEATURE_FILE_PATHS.items()
}

CHECKBOX_TASK_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
AC_ID_RE = re.compile(r"\bAC\d{3,}\b", re.IGNORECASE)
