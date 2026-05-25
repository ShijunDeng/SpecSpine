from __future__ import annotations

from typing import Any

from .benchmark_models import FeatureMetrics

__all__ = [
    "_generate_recommendations",
]


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
