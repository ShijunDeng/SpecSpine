from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"

IMPACT_TYPE_FEATURE = "feature"
IMPACT_TYPE_TEST = "test"
IMPACT_TYPE_CODE = "code"

SOURCE_GLOBS = ("src/**/*.py",)
TEST_GLOBS = ("tests/**/*.py",)


@dataclass(frozen=True)
class ImpactItem:
    type: str
    id: str
    path: str
    severity: str
    reason: str
    affected_acs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "affected_acs": list(self.affected_acs),
            "id": self.id,
            "path": self.path,
            "reason": self.reason,
            "severity": self.severity,
            "type": self.type,
        }
        return result


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
    "IMPACT_TYPE_CODE",
    "IMPACT_TYPE_FEATURE",
    "IMPACT_TYPE_TEST",
    "ImpactAnalysis",
    "ImpactItem",
    "SEVERITY_HIGH",
    "SEVERITY_LOW",
    "SEVERITY_MEDIUM",
    "SOURCE_GLOBS",
    "TEST_GLOBS",
]
