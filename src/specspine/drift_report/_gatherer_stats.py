from __future__ import annotations

from typing import Any

from ..drift_models import FeatureDriftRecord

__all__ = [
    "_compute_summary",
    "_compute_severity_distribution",
]


def _compute_severity_distribution(
    feature_tuple: tuple[FeatureDriftRecord, ...],
) -> dict[str, int]:
    severity_dist: dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "none": 0,
    }
    for f in feature_tuple:
        severity_dist[f.severity] = severity_dist.get(f.severity, 0) + 1
    return severity_dist


def _compute_summary(
    feature_tuple: tuple[FeatureDriftRecord, ...],
    severity_dist: dict[str, int],
) -> dict[str, Any]:
    total_events = sum(len(f.drift_events) for f in feature_tuple)
    drift_free = sum(1 for f in feature_tuple if f.severity == "none")

    return {
        "drift_events_total": total_events,
        "drift_free_count": drift_free,
        "features_scanned": len(feature_tuple),
        "severity_distribution": severity_dist,
    }
