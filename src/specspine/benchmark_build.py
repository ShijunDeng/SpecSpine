from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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

__all__ = [
    "build_benchmark_report",
    "_group_and_sort",
    "_generate_recommendations",
    "render_benchmark_json",
    "render_benchmark_text",
]


def _group_and_sort(metrics: list[FeatureMetrics], group_by: str) -> dict[str, list[FeatureMetrics]]:
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
    return groups


def _generate_recommendations(
    metrics: list[FeatureMetrics],
    aggregates: dict[str, Any],
    top_performers: list[dict[str, Any]],
    improvement_areas: list[dict[str, Any]],
    trends: dict[str, Any],
) -> tuple[str, ...]:
    recs: list[str] = []

    overall = aggregates.get("overall", {})
    avg_coverage = overall.get("avg_coverage", 0)
    if avg_coverage < 50:
        recs.append(
            f"Average AC coverage is {avg_coverage}%; prioritize linking test files to acceptance criteria"
        )

    avg_drift = overall.get("avg_drift_events", 0)
    if avg_drift > 2:
        recs.append(
            f"Average drift events per feature is {avg_drift}; review consistency scan results"
        )

    if improvement_areas:
        low_cov_features = [
            a["feature_id"]
            for a in improvement_areas
            if a.get("coverage_pct", 100) < 30
        ]
        if low_cov_features:
            recs.append(
                f"Features with coverage below 30%: {', '.join(low_cov_features[:3])}"
            )

    coverage_trend = trends.get("coverage_trend", "stable")
    if coverage_trend == "declining":
        recs.append("Overall coverage trend is declining; review quality gates")

    if not recs:
        recs.append("No critical recommendations; continue current practices")

    return tuple(recs[:5])


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


def render_benchmark_json(report: BenchmarkReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_benchmark_text(report: BenchmarkReport) -> str:
    lines: list[str] = []
    lines.append(f"SpecSpine Benchmark Report: {report.root}")
    lines.append(f"Features Analyzed: {report.feature_count}")
    lines.append("")

    overall = report.aggregates.get("overall", {})
    lines.append("Overall Aggregates:")
    lines.append(f"  Average AC count: {overall.get('avg_ac_count', 0)}")
    lines.append(f"  Average task count: {overall.get('avg_task_count', 0)}")
    lines.append(f"  Average test count: {overall.get('avg_test_count', 0)}")
    lines.append(f"  Average coverage: {overall.get('avg_coverage', 0)}%")
    lines.append(f"  Median coverage: {overall.get('median_coverage', 0)}%")
    lines.append(f"  P95 coverage: {overall.get('p95_coverage', 0)}%")
    lines.append(f"  Average drift events: {overall.get('avg_drift_events', 0)}")
    lines.append(f"  Average validation pass: {overall.get('avg_validation_pass', 0)}")
    lines.append(f"  Average validation fail: {overall.get('avg_validation_fail', 0)}")
    lines.append("")

    groups = report.aggregates.get("groups", {})
    if groups:
        lines.append("Groups:")
        for key, stats in sorted(groups.items()):
            lines.append(f"  {key}:")
            lines.append(f"    count: {stats['count']}")
            lines.append(f"    avg coverage: {stats['avg_coverage']}%")
            lines.append(f"    features: {', '.join(stats['features'][:5])}")
        lines.append("")

    if report.top_performers:
        lines.append("Top Performers:")
        for p in report.top_performers:
            lines.append(
                f"  {p['feature_id']}: score={p['score']}, "
                f"coverage={p['coverage_pct']}%, drift={p['drift_events']}"
            )
        lines.append("")

    if report.improvement_areas:
        lines.append("Improvement Areas:")
        for a in report.improvement_areas:
            lines.append(
                f"  {a['feature_id']}: score={a['score']}, "
                f"coverage={a['coverage_pct']}%, issue={a.get('primary_issue', 'needs_review')}"
            )
        lines.append("")

    trends = report.trends
    lines.append("Trends:")
    lines.append(f"  Coverage trend: {trends.get('coverage_trend', 'stable')}")
    lines.append(f"  Validation trend: {trends.get('validation_pass_rate_trend', 'stable')}")
    lines.append(f"  Drift trend: {trends.get('drift_frequency_trend', 'stable')}")
    cov_by_status = trends.get("coverage_by_status", {})
    if cov_by_status:
        lines.append("  Coverage by status:")
        for status, avg in sorted(cov_by_status.items()):
            lines.append(f"    {status}: {avg}%")
    lines.append("")

    if report.recommendations:
        lines.append("Recommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"  {i}. {rec}")
        lines.append("")

    lines.append("Safety Notes:")
    for note in report.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"
