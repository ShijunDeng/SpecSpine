from __future__ import annotations

from typing import Any

from .benchmark_models import FeatureMetrics
from .benchmark_compute_stats import _median, _percentile

__all__ = [
    "_aggregate_metrics",
]


def _aggregate_metrics(
    metrics: list[FeatureMetrics],
    group_by: str,
) -> dict[str, Any]:
    if not metrics:
        return {
            "groups": {},
            "overall": {
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
            },
        }

    ac_counts = [m.ac_count for m in metrics]
    task_counts = [m.task_count for m in metrics]
    test_counts = [m.test_count for m in metrics]
    coverage_vals = [m.coverage_pct for m in metrics]
    validation_pass_vals = [m.validation_pass for m in metrics]
    validation_fail_vals = [m.validation_fail for m in metrics]
    consistency_fail_vals = [m.consistency_fail for m in metrics]
    drift_vals = [m.drift_events for m in metrics]
    duration_vals = [m.lifecycle_duration_days for m in metrics]

    overall = {
        "avg_ac_count": round(sum(ac_counts) / len(ac_counts), 2),
        "avg_consistency_fail": round(sum(consistency_fail_vals) / len(consistency_fail_vals), 2),
        "avg_coverage": round(sum(coverage_vals) / len(coverage_vals), 2),
        "avg_drift_events": round(sum(drift_vals) / len(drift_vals), 2),
        "avg_lifecycle_duration_days": round(sum(duration_vals) / len(duration_vals), 2),
        "avg_task_count": round(sum(task_counts) / len(task_counts), 2),
        "avg_test_count": round(sum(test_counts) / len(test_counts), 2),
        "avg_validation_fail": round(sum(validation_fail_vals) / len(validation_fail_vals), 2),
        "avg_validation_pass": round(sum(validation_pass_vals) / len(validation_pass_vals), 2),
        "median_ac_count": round(_median(ac_counts), 2),
        "median_consistency_fail": round(_median(consistency_fail_vals), 2),
        "median_coverage": round(_median(coverage_vals), 2),
        "median_drift_events": round(_median(drift_vals), 2),
        "median_lifecycle_duration_days": round(_median(duration_vals), 2),
        "median_task_count": round(_median(task_counts), 2),
        "median_test_count": round(_median(test_counts), 2),
        "median_validation_fail": round(_median(validation_fail_vals), 2),
        "median_validation_pass": round(_median(validation_pass_vals), 2),
        "p95_coverage": round(_percentile(coverage_vals, 95), 2),
        "p95_lifecycle_duration_days": round(_percentile(duration_vals, 95), 2),
        "p95_test_count": round(_percentile(test_counts, 95), 2),
        "total_features": len(metrics),
    }

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

    return {
        "groups": group_stats,
        "overall": overall,
    }
