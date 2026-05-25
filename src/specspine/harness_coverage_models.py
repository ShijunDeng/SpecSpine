from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "GOVERNED_DIMENSIONS",
    "DIMENSION_SENSOR_MAP",
    "MATURITY_LABELS",
    "HarnessDimensionCoverage",
    "HarnessCoverageReport",
]

GOVERNED_DIMENSIONS = (
    "verification",
    "coverage",
    "grading",
    "validation",
    "consistency",
    "hygiene",
    "security",
    "change_risk",
)

DIMENSION_SENSOR_MAP = {
    "verification": "verification_matrix",
    "coverage": "coverage_debt",
    "grading": "grading_rubric",
    "validation": "validation_contract",
    "consistency": "consistency_scan",
    "hygiene": "hygiene_scan",
    "security": "security_cues",
    "change_risk": "change_risk",
}

MATURITY_LABELS = {
    0: "none",
    1: "initial",
    2: "managed",
    3: "defined",
    4: "optimized",
    5: "mastered",
}


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
