from __future__ import annotations

from typing import Any

from ..benchmark_models import FeatureMetrics
from ..benchmark_issue_identifiers import _primary_issue


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
    "_identify_improvement_areas",
]
