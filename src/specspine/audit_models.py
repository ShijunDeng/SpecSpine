from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "AC_ID_RE",
    "AuditEvent",
    "AuditTrail",
    "COV_LINK_RE",
    "ComplianceReport",
    "FEATURE_ID_RE",
    "GIT_LOG_DATE_RE",
    "LIFECYCLE_STATUS_RE",
    "QUALITY_CHECK_RE",
    "TASK_ID_RE",
]

GIT_LOG_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
LIFECYCLE_STATUS_RE = re.compile(r"Status:\s*(\S+)", re.IGNORECASE)
FEATURE_ID_RE = re.compile(r"Feature\s+ID:\s*([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")
QUALITY_CHECK_RE = re.compile(r"(QC\d{3})")
COV_LINK_RE = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    timestamp: str
    feature_id: str
    description: str
    evidence_hash: str = ""
    actor: str = ""

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "actor": self.actor,
            "description": self.description,
            "evidence_hash": self.evidence_hash,
            "event_type": self.event_type,
            "feature_id": self.feature_id,
            "timestamp": self.timestamp,
        }
        return result


@dataclass(frozen=True)
class AuditTrail:
    feature_id: str
    events: tuple[AuditEvent, ...] = ()
    lifecycle_transitions: tuple[dict[str, str], ...] = ()
    validation_evidence: dict[str, Any] = field(default_factory=dict)
    drift_history: tuple[dict[str, Any], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "drift_history": [dict(d) for d in self.drift_history],
            "events": [e.as_dict() for e in self.events],
            "feature_id": self.feature_id,
            "lifecycle_transitions": [dict(t) for t in self.lifecycle_transitions],
            "validation_evidence": dict(self.validation_evidence),
        }


@dataclass(frozen=True)
class ComplianceReport:
    root: Path
    audit_date: str
    scope: str
    features: tuple[AuditTrail, ...]
    compliance_summary: dict[str, Any]
    evidence_hashes: tuple[str, ...]
    recommendations: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "audit_date": self.audit_date,
            "compliance_summary": dict(self.compliance_summary),
            "evidence_hashes": list(self.evidence_hashes),
            "features": [f.as_dict() for f in self.features],
            "recommendations": list(self.recommendations),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "scope": self.scope,
        }
