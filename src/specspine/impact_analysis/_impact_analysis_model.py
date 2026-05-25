from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._impact_item_model import ImpactItem


@dataclass(frozen=True)
class ImpactAnalysis:
    feature_id: str
    total_affected: int
    impacted_features: tuple[ImpactItem, ...]
    impacted_tests: tuple[ImpactItem, ...]
    impacted_code: tuple[ImpactItem, ...]
    risk_score: int
    mitigation_steps: tuple[str, ...]
    safety_notes: tuple[str, ...]
    recommended_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "impacted_code": [item.as_dict() for item in self.impacted_code],
            "impacted_features": [
                item.as_dict() for item in self.impacted_features
            ],
            "impacted_tests": [item.as_dict() for item in self.impacted_tests],
            "mitigation_steps": list(self.mitigation_steps),
            "recommended_commands": list(self.recommended_commands),
            "risk_score": self.risk_score,
            "safety_notes": list(self.safety_notes),
            "total_affected": self.total_affected,
        }


__all__ = [
    "ImpactAnalysis",
]
