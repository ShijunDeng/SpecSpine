from __future__ import annotations

from typing import Any

from ..benchmark_models import FeatureMetrics

__all__ = [
    "_aggregate_coverage_by_status",
]


def _aggregate_coverage_by_status(metrics: list[FeatureMetrics]) -> dict[str, Any]:
    status_coverage: dict[str, list[float]] = {}
    for m in metrics:
        status_coverage.setdefault(m.status, []).append(m.coverage_pct)

    coverage_by_status = {}
    for status, vals in sorted(status_coverage.items()):
        coverage_by_status[status] = round(sum(vals) / len(vals), 2)
    return coverage_by_status
