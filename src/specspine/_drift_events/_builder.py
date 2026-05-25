from __future__ import annotations

from pathlib import Path

from .._drift_git_utils import _run_git_log, GIT_LOG_DATE_RE
from ._path_resolver import _resolve_feature_paths
from ._event_classifier import _classify_event_type, _classify_severity

__all__ = [
    "_build_drift_history",
]


def _build_drift_history(slug: str, root: Path, since: str | None) -> list:
    from ..drift_models import DriftEvent

    events: list[DriftEvent] = []
    rel_paths = _resolve_feature_paths(root, slug)
    if not rel_paths:
        return events

    lines = _run_git_log(root, rel_paths)
    for line in lines:
        parts = line.split("|", 2)
        if len(parts) < 2:
            continue
        commit_hash, date_str = parts[0], parts[1]
        message = parts[2] if len(parts) > 2 else ""

        if since is not None:
            date_match = GIT_LOG_DATE_RE.match(date_str)
            if date_match:
                commit_date = date_match.group(0)
                if commit_date < since:
                    continue

        event_type = _classify_event_type(slug, rel_paths)
        severity = _classify_severity(message)

        events.append(
            DriftEvent(
                event_type=event_type,
                severity=severity,
                timestamp=date_str.strip(),
                description=f"Commit {commit_hash[:8]}: {message}",
            )
        )

    return events
