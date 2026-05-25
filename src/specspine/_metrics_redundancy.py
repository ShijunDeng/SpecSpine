from __future__ import annotations

from typing import Any

from .harness_coverage_models import HarnessDimensionCoverage

__all__ = [
    "_detect_redundancy",
]


def _detect_redundancy(dimensions: list[HarnessDimensionCoverage]) -> list[dict[str, Any]]:
    redundancy_info: list[dict[str, Any]] = []
    for d in dimensions:
        if d.redundant_sensors:
            redundancy_info.append({
                "dimension": d.dimension_name,
                "redundant_sensors": list(d.redundant_sensors),
            })
    return redundancy_info
