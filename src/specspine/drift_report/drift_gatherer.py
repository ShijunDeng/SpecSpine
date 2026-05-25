from __future__ import annotations

from pathlib import Path
from typing import Any

from ..drift_analysis import _correlate_cross_feature_drift, _parse_feature_drift
from ..drift_models import FeatureDriftRecord
from ..drift_history import _git_commit, GIT_LOG_DATE_RE
from ..features import (
    list_feature_bundles,
    validate_feature_slug,
)

__all__ = [
    "_gather_feature_drift_records",
]


def _gather_feature_drift_records(
    resolved_root: Path,
    *,
    feature_filter: str | None = None,
    baseline: str | None = None,
    since: str | None = None,
) -> tuple[tuple[FeatureDriftRecord, ...], dict[str, Any], dict[str, Any], tuple[dict[str, Any], ...]]:
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)

    discovered = list_feature_bundles(resolved_root)
    discovered_slugs = {str(f["slug"]) for f in discovered}

    if feature_filter is not None:
        slugs = (feature_filter,)
    else:
        slugs = tuple(sorted(discovered_slugs))

    feature_records: list[FeatureDriftRecord] = []
    for slug in slugs:
        record = _parse_feature_drift(slug, resolved_root, baseline, since)
        feature_records.append(record)

    _correlate_cross_feature_drift(feature_records, resolved_root)

    feature_tuple = tuple(sorted(feature_records, key=lambda f: f.feature_id))

    severity_dist: dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "none": 0,
    }
    for f in feature_tuple:
        severity_dist[f.severity] = severity_dist.get(f.severity, 0) + 1

    total_events = sum(len(f.drift_events) for f in feature_tuple)
    drift_free = sum(1 for f in feature_tuple if f.severity == "none")

    trends: tuple[dict[str, Any], ...] = ()
    if since is not None:
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
        trends = tuple(trend_entries)

    summary = {
        "drift_events_total": total_events,
        "drift_free_count": drift_free,
        "features_scanned": len(feature_tuple),
        "severity_distribution": severity_dist,
    }

    scan_metadata = {
        "baseline": baseline,
        "git_commit": _git_commit(resolved_root),
        "since": since,
    }

    return feature_tuple, summary, scan_metadata, trends
