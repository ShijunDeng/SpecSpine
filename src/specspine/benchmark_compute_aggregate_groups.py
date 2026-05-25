from __future__ import annotations

from typing import Any

from .benchmark_models import FeatureMetrics
from .benchmark_compute_stats import _median

__all__ = [
    "_compute_group_stats",
]


def _compute_group_stats(
    metrics: list[FeatureMetrics],
    group_by: str,
) -> dict[str, Any]:
    groups: dict[str, list[FeatureMetrics]] = {}
    for m in metrics:
        if group_by == "priority":
            key = m.priority
        elif group_by == "status":
            key = m.status
        elif group_by == "project":
            key = m.project
        elif group_by == "effort":
            key = m.effort
        else:
            key = "unknown"
        groups.setdefault(key, []).append(m)

    group_stats: dict[str, Any] = {}
    for key, group_metrics in sorted(groups.items()):
        g_cov = [m.coverage_pct for m in group_metrics]
        g_ac = [m.ac_count for m in group_metrics]
        g_drift = [m.drift_events for m in group_metrics]
        group_stats[key] = {
            "count": len(group_metrics),
            "avg_coverage": round(sum(g_cov) / len(g_cov), 2) if g_cov else 0.0,
            "avg_ac_count": round(sum(g_ac) / len(g_ac), 2) if g_ac else 0.0,
            "avg_drift_events": round(sum(g_drift) / len(g_drift), 2) if g_drift else 0.0,
            "median_coverage": round(_median(g_cov), 2),
            "features": [m.feature_id for m in group_metrics],
        }

    return group_stats
