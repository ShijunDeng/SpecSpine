from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "HarnessDimensionCoverage",
    "HarnessCoverageReport",
]


@dataclass(frozen=True)
class HarnessDimensionCoverage:
    dimension_name: str
    sensor_count: int
    pass_count: int
    coverage_pct: float
    missing_sensors: tuple[str, ...] = ()
    redundant_sensors: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "coverage_pct": round(self.coverage_pct, 2),
            "dimension_name": self.dimension_name,
            "missing_sensors": list(self.missing_sensors),
            "pass_count": self.pass_count,
            "redundant_sensors": list(self.redundant_sensors),
            "sensor_count": self.sensor_count,
        }


@dataclass(frozen=True)
class HarnessCoverageReport:
    feature_id: str
    dimensions: tuple[HarnessDimensionCoverage, ...]
    maturity_score: int
    blind_spots: tuple[str, ...]
    improvement_plan: tuple[str, ...]
    baseline_comparison: dict[str, Any] = field(default_factory=dict)
    safety_notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "baseline_comparison": self.baseline_comparison,
            "blind_spots": list(self.blind_spots),
            "dimensions": [d.as_dict() for d in self.dimensions],
            "feature_id": self.feature_id,
            "improvement_plan": list(self.improvement_plan),
            "maturity_score": self.maturity_score,
            "safety_notes": list(self.safety_notes),
        }
