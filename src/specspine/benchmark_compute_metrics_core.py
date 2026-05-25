from __future__ import annotations

from pathlib import Path

from .benchmark_models import FeatureMetrics
from .features import (
    InvalidFeatureSlug,
    get_feature_status,
    read_feature_metadata,
    validate_feature_slug,
)
from ._benchmark_file_metrics import (
    AC_ID_RE,
    TASK_ID_RE,
    COV_LINK_DONE_RE,
    COV_LINK_TOTAL_RE,
    _read_text,
    _count_pattern,
    _count_feature_artifacts,
)
from ._benchmark_quality_gatherer import _gather_quality_metrics

__all__ = [
    "AC_ID_RE",
    "TASK_ID_RE",
    "COV_LINK_DONE_RE",
    "COV_LINK_TOTAL_RE",
    "_read_text",
    "_count_pattern",
    "_compute_feature_metrics",
]


def _compute_feature_metrics(slug: str, root: Path) -> FeatureMetrics:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    status_report = get_feature_status(resolved_root, slug)
    status = status_report.status or "unknown"

    metadata = read_feature_metadata(resolved_root, slug)
    priority = metadata.priority
    effort = metadata.effort
    project = metadata.project

    artifact_counts = _count_feature_artifacts(slug, root)
    quality_metrics = _gather_quality_metrics(slug, resolved_root)

    lifecycle_duration_days = 0.0

    return FeatureMetrics(
        feature_id=slug,
        status=status,
        priority=priority,
        effort=effort,
        project=project,
        ac_count=artifact_counts["ac_count"],
        task_count=artifact_counts["task_count"],
        test_count=artifact_counts["test_count"],
        coverage_pct=artifact_counts["coverage_pct"],
        validation_pass=quality_metrics["validation_pass"],
        validation_fail=quality_metrics["validation_fail"],
        consistency_fail=quality_metrics["consistency_fail"],
        drift_events=quality_metrics["drift_events"],
        lifecycle_duration_days=lifecycle_duration_days,
    )
