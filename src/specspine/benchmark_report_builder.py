from __future__ import annotations

from pathlib import Path

from .benchmark_models import FeatureMetrics, BenchmarkReport, VALID_GROUP_BY, SAFETY_NOTES
from .features import (
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)
from .benchmark_compute import (
    _compute_feature_metrics,
    _aggregate_metrics,
    _identify_top_performers,
    _identify_improvement_areas,
    _compute_trends,
)
from .benchmark_recommendations import _generate_recommendations

__all__ = [
    "build_benchmark_report",
]


def build_benchmark_report(
    root: Path,
    feature_filter: str | None = None,
    group_by: str = "priority",
) -> BenchmarkReport:
    resolved_root = root.expanduser().resolve()

    if group_by not in VALID_GROUP_BY:
        group_by = "priority"

    bundles = list_feature_bundles(resolved_root)
    slugs = [b["slug"] for b in bundles]

    if feature_filter:
        try:
            validate_feature_slug(feature_filter)
            if feature_filter in slugs:
                slugs = [feature_filter]
            else:
                slugs = []
        except InvalidFeatureSlug:
            slugs = []

    metrics: list[FeatureMetrics] = []
    for slug in sorted(slugs):
        try:
            m = _compute_feature_metrics(slug, resolved_root)
            metrics.append(m)
        except (InvalidFeatureSlug, OSError):
            continue

    aggregates = _aggregate_metrics(metrics, group_by)
    top_performers = _identify_top_performers(metrics)
    improvement_areas = _identify_improvement_areas(metrics)
    trends = _compute_trends(metrics)
    recommendations = _generate_recommendations(
        metrics, aggregates, top_performers, improvement_areas, trends
    )

    return BenchmarkReport(
        root=str(resolved_root),
        feature_count=len(metrics),
        metrics=tuple(metrics),
        aggregates=aggregates,
        top_performers=tuple(top_performers),
        improvement_areas=tuple(improvement_areas),
        trends=trends,
        recommendations=recommendations,
        safety_notes=SAFETY_NOTES,
    )
