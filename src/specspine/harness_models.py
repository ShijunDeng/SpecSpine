from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "HarnessFeedbackSensor",
    "HarnessFeedbackReport",
    "HarnessQualityReport",
    "RepairStrategy",
    "REPAIR_TYPES",
    "SENSOR_CATEGORIES",
]

SENSOR_CATEGORIES = ("computational", "inferential")

REPAIR_TYPES = (
    "spec_update",
    "quality_update",
    "sensor_failure",
)


@dataclass(frozen=True)
class HarnessFeedbackSensor:
    sensor_type: str
    name: str
    status: str
    output: dict[str, Any]
    ac_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "ac_ids": list(self.ac_ids),
            "name": self.name,
            "output": dict(self.output),
            "sensor_type": self.sensor_type,
            "status": self.status,
        }


@dataclass(frozen=True)
class RepairStrategy:
    ac_id: str
    target_file: str
    edit_description: str
    verification_command: str
    success_criteria: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "edit_description": self.edit_description,
            "success_criteria": self.success_criteria,
            "target_file": self.target_file,
            "verification_command": self.verification_command,
        }


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


@dataclass(frozen=True)
class HarnessFeedbackReport:
    feature_id: str
    status: str
    sensors: tuple[HarnessFeedbackSensor, ...]
    repair_strategies: tuple[RepairStrategy, ...]
    root_causes: dict[str, Any]
    steering_summary: dict[str, Any]
    harness_quality: HarnessQualityReport | None
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "feature_id": self.feature_id,
            "repair_strategies": [s.as_dict() for s in self.repair_strategies],
            "root_causes": dict(self.root_causes),
            "safety_notes": list(self.safety_notes),
            "sensors": [s.as_dict() for s in self.sensors],
            "status": self.status,
            "steering_summary": dict(self.steering_summary),
        }
        if self.harness_quality is not None:
            payload["harness_quality"] = self.harness_quality.as_dict()
        return payload
