from __future__ import annotations

from typing import Any

__all__ = [
    "_empty_overall_defaults",
]


def _empty_overall_defaults() -> dict[str, Any]:
    return {
        "avg_ac_count": 0.0,
        "avg_consistency_fail": 0.0,
        "avg_coverage": 0.0,
        "avg_drift_events": 0.0,
        "avg_lifecycle_duration_days": 0.0,
        "avg_task_count": 0.0,
        "avg_test_count": 0.0,
        "avg_validation_fail": 0.0,
        "avg_validation_pass": 0.0,
        "median_ac_count": 0.0,
        "median_consistency_fail": 0.0,
        "median_coverage": 0.0,
        "median_drift_events": 0.0,
        "median_lifecycle_duration_days": 0.0,
        "median_task_count": 0.0,
        "median_test_count": 0.0,
        "median_validation_fail": 0.0,
        "median_validation_pass": 0.0,
        "p95_coverage": 0.0,
        "p95_lifecycle_duration_days": 0.0,
        "p95_test_count": 0.0,
        "total_features": 0,
    }
