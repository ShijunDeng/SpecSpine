from __future__ import annotations

from ..features import (
    FEATURE_FILE_PATHS,
)

__all__ = [
    "_classify_event_type",
    "_classify_severity",
]

_SEVERITY_DELETE_KEYWORDS = ("remove", "delete", "drop")
_SEVERITY_ADD_KEYWORDS = ("add", "new", "create")


def _classify_event_type(slug: str, rel_paths: list[str]) -> str:
    for kind in ("spec", "execution", "quality"):
        rel = FEATURE_FILE_PATHS.get(kind, "").format(slug=slug)
        if rel in " ".join(rel_paths):
            return kind
    return "spec"


def _classify_severity(message: str) -> str:
    message_lower = message.lower()
    if any(kw in message_lower for kw in _SEVERITY_DELETE_KEYWORDS):
        return "high"
    if any(kw in message_lower for kw in _SEVERITY_ADD_KEYWORDS):
        return "low"
    return "medium"
