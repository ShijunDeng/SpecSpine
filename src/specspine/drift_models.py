from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__all__ = [
    "DriftEvent",
    "FeatureDriftRecord",
    "DriftAuditReport",
    "_now_iso",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class DriftEvent:
    event_type: str
    severity: str
    timestamp: str
    description: str
    affected_acs: tuple[str, ...] = ()
    affected_tasks: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "affected_acs": list(self.affected_acs),
            "affected_tasks": list(self.affected_tasks),
            "description": self.description,
            "event_type": self.event_type,
            "severity": self.severity,
            "timestamp": self.timestamp,
        }
        return result


@dataclass(frozen=True)
class FeatureDriftRecord:
    feature_id: str
    severity: str
    spec_drift: tuple[DriftEvent, ...]
    code_drift: tuple[DriftEvent, ...]
    test_drift: tuple[DriftEvent, ...]
    quality_drift: tuple[DriftEvent, ...]
    drift_events: tuple[DriftEvent, ...]
    cascade_risk: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "cascade_risk": self.cascade_risk,
            "code_drift": [e.as_dict() for e in self.code_drift],
            "drift_events": [e.as_dict() for e in self.drift_events],
            "feature_id": self.feature_id,
            "quality_drift": [e.as_dict() for e in self.quality_drift],
            "severity": self.severity,
            "spec_drift": [e.as_dict() for e in self.spec_drift],
            "test_drift": [e.as_dict() for e in self.test_drift],
        }


@dataclass(frozen=True)
class DriftAuditReport:
    root: Path
    scan_metadata: dict[str, Any]
    features: tuple[FeatureDriftRecord, ...]
    summary: dict[str, Any]
    trends: tuple[dict[str, Any], ...]
    compliance: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "compliance": dict(self.compliance),
            "features": [f.as_dict() for f in self.features],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "scan_metadata": dict(self.scan_metadata),
            "summary": dict(self.summary),
            "trends": [dict(t) for t in self.trends],
        }
