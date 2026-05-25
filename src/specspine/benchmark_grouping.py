from __future__ import annotations

from .benchmark_models import FeatureMetrics

__all__ = [
    "_group_and_sort",
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
