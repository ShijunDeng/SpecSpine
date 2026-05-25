from __future__ import annotations

from typing import Any

from .benchmark_models import FeatureMetrics
from .benchmark_compute_aggregate_overall import _compute_overall_metrics
from .benchmark_compute_aggregate_groups import _compute_group_stats

__all__ = [
    "_aggregate_metrics",
    "_compute_overall_metrics",
    "_compute_group_stats",
]


def _aggregate_metrics(
    metrics: list[FeatureMetrics],
    group_by: str,
) -> dict[str, Any]:
    overall = _compute_overall_metrics(metrics)
    groups = _compute_group_stats(metrics, group_by)
    return {
        "groups": groups,
        "overall": overall,
    }
