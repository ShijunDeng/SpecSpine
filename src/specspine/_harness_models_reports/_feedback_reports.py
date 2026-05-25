from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .._harness_models_sensors import HarnessFeedbackSensor
from ._quality_reports import HarnessQualityReport
from ._strategies import RepairStrategy

__all__ = [
    "HarnessFeedbackReport",
]


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
