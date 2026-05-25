from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._audit_trail import AuditTrail

__all__ = [
    "ComplianceReport",
]


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
