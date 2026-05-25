from __future__ import annotations

from typing import Any

from ..drift_history import _git_commit, GIT_LOG_DATE_RE
from ..drift_models import FeatureDriftRecord

__all__ = [
    "_compute_trends",
    "_compute_scan_metadata",
]


def _compute_trends(
    feature_tuple: tuple[FeatureDriftRecord, ...],
    since: str | None,
) -> tuple[dict[str, Any], ...]:
    if since is None:
        return ()

    trend_entries: list[dict[str, Any]] = []
    date_events: dict[str, int] = {}
    for f in feature_tuple:
        for ev in f.drift_events:
            date_match = GIT_LOG_DATE_RE.match(ev.timestamp)
            if date_match:
                day = date_match.group(0)
                date_events[day] = date_events.get(day, 0) + 1
    for day in sorted(date_events):
        trend_entries.append({"date": day, "drift_events": date_events[day]})
    return tuple(trend_entries)


def _compute_scan_metadata(
    resolved_root: Any,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "baseline": metadata.get("baseline"),
        "git_commit": _git_commit(resolved_root),
        "since": metadata.get("since"),
    }
