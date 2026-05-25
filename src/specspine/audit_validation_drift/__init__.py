from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import feature_bundle_paths
from ._drift_git import _fetch_git_log_lines
from ._drift_classifier import _build_drift_event, _classify_event_type, _classify_severity

__all__ = [
    "_build_drift_history",
]


def _build_drift_history(slug: str, root: Path, since: str | None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return events

    rel_paths = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    if not rel_paths:
        return events

    git_entries = _fetch_git_log_lines(root, rel_paths)
    if not git_entries:
        return events

    for entry in git_entries:
        date_str = entry["date_str"]
        message = entry["message"]
        commit_hash = entry["commit_hash"]

        if since is not None:
            from ..audit_models import GIT_LOG_DATE_RE
            date_match = GIT_LOG_DATE_RE.match(date_str)
            if date_match:
                commit_date = date_match.group(0)
                if commit_date < since:
                    continue

        event_type = _classify_event_type(slug, rel_paths)
        severity = _classify_severity(message)

        events.append(_build_drift_event(commit_hash, date_str, message, event_type, severity))

    return events
