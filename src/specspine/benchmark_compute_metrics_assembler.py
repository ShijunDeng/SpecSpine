from __future__ import annotations

from pathlib import Path

from .benchmark_models import FeatureMetrics
from .benchmark_compute_metrics_feature_info import gather_feature_info
from ._benchmark_file_metrics import _count_feature_artifacts
from ._benchmark_quality_gatherer import _gather_quality_metrics

__all__ = [
    "_compute_feature_metrics",
]


def _compute_feature_metrics(slug: str, root: Path) -> FeatureMetrics:
    info = gather_feature_info(slug, root)
    artifact_counts = _count_feature_artifacts(info.slug, root)
    quality_metrics = _gather_quality_metrics(info.slug, root.expanduser().resolve())

    return FeatureMetrics(
        feature_id=info.slug,
        status=info.status,
        priority=info.priority,
        effort=info.effort,
        project=info.project,
        ac_count=artifact_counts["ac_count"],
        task_count=artifact_counts["task_count"],
        test_count=artifact_counts["test_count"],
        coverage_pct=artifact_counts["coverage_pct"],
        validation_pass=quality_metrics["validation_pass"],
        validation_fail=quality_metrics["validation_fail"],
        consistency_fail=quality_metrics["consistency_fail"],
        drift_events=quality_metrics["drift_events"],
        lifecycle_duration_days=0.0,
    )
