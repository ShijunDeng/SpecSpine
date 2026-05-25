from __future__ import annotations

from typing import Any

from ..benchmark_models import FeatureMetrics

__all__ = [
    "_aggregate_drift_by_priority",
]


def _aggregate_drift_by_priority(metrics: list[FeatureMetrics]) -> dict[str, Any]:
    priority_drift: dict[str, list[int]] = {}
    for m in metrics:
        priority_drift.setdefault(m.priority, []).append(m.drift_events)

    drift_by_priority = {}
    for prio, vals in sorted(priority_drift.items()):
        drift_by_priority[prio] = round(sum(vals) / len(vals), 2)
    return drift_by_priority
