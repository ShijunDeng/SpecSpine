from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "HarnessQualityReport",
]


@dataclass(frozen=True)
class HarnessQualityReport:
    feature_id: str
    governed_dimensions: tuple[str, ...]
    sensor_count: int
    harness_coverage_pct: float
    dimension_scores: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension_scores": dict(self.dimension_scores),
            "feature_id": self.feature_id,
            "governed_dimensions": list(self.governed_dimensions),
            "harness_coverage_pct": round(self.harness_coverage_pct, 2),
            "sensor_count": self.sensor_count,
        }
