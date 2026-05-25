from __future__ import annotations

from typing import Any

from ..features import FEATURE_FILE_PATHS

__all__ = [
    "_classify_event_type",
    "_classify_severity",
]


def _classify_event_type(slug: str, rel_paths: list[str]) -> str:
    event_type = "unknown"
    for kind in ("spec", "execution", "quality"):
        rel = FEATURE_FILE_PATHS.get(kind, "").format(slug=slug)
        if rel in " ".join(rel_paths):
            event_type = kind
            break
    return event_type


def _classify_severity(message: str) -> str:
    severity = "medium"
    if any(kw in message.lower() for kw in ("remove", "delete", "drop")):
        severity = "high"
    elif any(kw in message.lower() for kw in ("add", "new", "create")):
        severity = "low"
    return severity


def _build_drift_event(
    commit_hash: str,
    date_str: str,
    message: str,
    event_type: str,
    severity: str,
) -> dict[str, Any]:
    return {
        "commit": commit_hash[:8],
        "date": date_str,
        "event_type": event_type,
        "message": message,
        "severity": severity,
    }
