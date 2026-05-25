from __future__ import annotations

from typing import Any

from .benchmark_models import FeatureMetrics
from .benchmark_compute_stats import _median

__all__ = [
    "_compute_trends",
]


def _compute_trends(metrics: list[FeatureMetrics]) -> dict[str, Any]:
    if not metrics:
        return {
            "coverage_trend": "stable",
            "validation_pass_rate_trend": "stable",
            "drift_frequency_trend": "stable",
            "coverage_by_status": {},
            "drift_by_priority": {},
        }

    status_coverage: dict[str, list[float]] = {}
    priority_drift: dict[str, list[int]] = {}

    for m in metrics:
        status_coverage.setdefault(m.status, []).append(m.coverage_pct)
        priority_drift.setdefault(m.priority, []).append(m.drift_events)

    coverage_by_status = {}
    for status, vals in sorted(status_coverage.items()):
        coverage_by_status[status] = round(sum(vals) / len(vals), 2)

    drift_by_priority = {}
    for prio, vals in sorted(priority_drift.items()):
        drift_by_priority[prio] = round(sum(vals) / len(vals), 2)

    all_coverage = [m.coverage_pct for m in metrics]
    avg_cov = sum(all_coverage) / len(all_coverage) if all_coverage else 0

    total_drift = sum(m.drift_events for m in metrics)
    total_val_pass = sum(m.validation_pass for m in metrics)
    total_val_fail = sum(m.validation_fail for m in metrics)
    val_pass_rate = (
        total_val_pass / (total_val_pass + total_val_fail)
        if (total_val_pass + total_val_fail) > 0
        else 1.0
    )

    coverage_trend = "stable"
    if avg_cov >= 80:
        coverage_trend = "healthy"
    elif avg_cov < 30:
        coverage_trend = "declining"

    drift_trend = "stable"
    avg_drift = total_drift / len(metrics) if metrics else 0
    if avg_drift > 5:
        drift_trend = "increasing"
    elif avg_drift < 1:
        drift_trend = "improving"

    val_trend = "stable"
    if val_pass_rate >= 0.9:
        val_trend = "healthy"
    elif val_pass_rate < 0.5:
        val_trend = "declining"

    return {
        "coverage_trend": coverage_trend,
        "validation_pass_rate_trend": val_trend,
        "drift_frequency_trend": drift_trend,
        "coverage_by_status": coverage_by_status,
        "drift_by_priority": drift_by_priority,
    }
