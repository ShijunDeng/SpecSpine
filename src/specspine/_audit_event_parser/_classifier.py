from __future__ import annotations

from ..audit_models import GIT_LOG_DATE_RE

__all__ = [
    "_classify_event_type",
    "_filter_by_since",
]


def _classify_event_type(message: str) -> str:
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ("status", "lifecycle", "transition")):
        return "lifecycle"
    if any(kw in msg_lower for kw in ("validat", "verif")):
        return "validation"
    if any(kw in msg_lower for kw in ("test", "coverage")):
        return "test"
    if any(kw in msg_lower for kw in ("drift", "consisten")):
        return "consistency"
    return "file_change"


def _filter_by_since(date_str: str, since: str | None) -> bool:
    if since is None:
        return True
    date_match = GIT_LOG_DATE_RE.match(date_str)
    if date_match:
        commit_date = date_match.group(0)
        if commit_date < since:
            return False
    return True
