from __future__ import annotations

from .harness_coverage_models import HarnessDimensionCoverage

__all__ = [
    "_detect_blind_spots",
]


def _detect_blind_spots(dimensions: list[HarnessDimensionCoverage]) -> list[str]:
    return [
        d.dimension_name
        for d in dimensions
        if d.sensor_count == 0
    ]
