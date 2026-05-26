from __future__ import annotations

from typing import Any

from ..benchmark_models import FeatureMetrics


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


__all__ = [
    "_identify_top_performers",
]
