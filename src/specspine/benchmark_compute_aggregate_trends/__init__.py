from __future__ import annotations

from typing import Any

from ..benchmark_models import FeatureMetrics
from ._trend_classifiers import (
    _classify_coverage_trend,
    _classify_drift_trend,
    _classify_validation_trend,
)
from ._coverage_aggregator import (
    _aggregate_coverage_by_status,
)
from ._drift_aggregator import (
    _aggregate_drift_by_priority,
)

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

    coverage_by_status = _aggregate_coverage_by_status(metrics)
    drift_by_priority = _aggregate_drift_by_priority(metrics)

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

    coverage_trend = _classify_coverage_trend(avg_cov)
    avg_drift = total_drift / len(metrics) if metrics else 0
    drift_trend = _classify_drift_trend(avg_drift)
    val_trend = _classify_validation_trend(val_pass_rate)

    return {
        "coverage_trend": coverage_trend,
        "validation_pass_rate_trend": val_trend,
        "drift_frequency_trend": drift_trend,
        "coverage_by_status": coverage_by_status,
        "drift_by_priority": drift_by_priority,
    }
