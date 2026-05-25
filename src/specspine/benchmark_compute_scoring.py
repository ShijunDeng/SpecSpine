from __future__ import annotations

from typing import Any

from .benchmark_models import FeatureMetrics


def _primary_issue(m: FeatureMetrics) -> str:
    issues = []
    if m.coverage_pct < 50:
        issues.append("low_coverage")
    if m.drift_events > 2:
        issues.append("high_drift")
    if m.consistency_fail > 0:
        issues.append("consistency_failures")
    if m.ac_count > 0 and m.test_count == 0:
        issues.append("no_test_links")
    return issues[0] if issues else "needs_review"


def _identify_top_performers(metrics: list[FeatureMetrics]) -> list[dict[str, Any]]:
    if not metrics:
        return []

    scored = []
    for m in metrics:
        score = (
            m.coverage_pct * 0.4
            + max(0, 100 - m.drift_events * 10) * 0.3
            + max(0, 100 - m.consistency_fail * 20) * 0.3
        )
        scored.append((score, m))

    scored.sort(key=lambda x: -x[0])

    top = scored[:5]
    return [
        {
            "feature_id": m.feature_id,
            "score": round(score, 2),
            "coverage_pct": m.coverage_pct,
            "drift_events": m.drift_events,
            "consistency_fail": m.consistency_fail,
        }
        for score, m in top
    ]


def _identify_improvement_areas(metrics: list[FeatureMetrics]) -> list[dict[str, Any]]:
    if not metrics:
        return []

    scored = []
    for m in metrics:
        score = (
            (100 - m.coverage_pct) * 0.4
            + m.drift_events * 10 * 0.3
            + m.consistency_fail * 20 * 0.3
        )
        scored.append((score, m))

    scored.sort(key=lambda x: -x[0])

    bottom = scored[:5]
    return [
        {
            "feature_id": m.feature_id,
            "score": round(score, 2),
            "coverage_pct": m.coverage_pct,
            "drift_events": m.drift_events,
            "consistency_fail": m.consistency_fail,
            "primary_issue": _primary_issue(m),
        }
        for score, m in bottom
    ]


__all__ = [
    "_primary_issue",
    "_identify_top_performers",
    "_identify_improvement_areas",
]
