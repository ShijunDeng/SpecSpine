from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._audit_event import AuditEvent

__all__ = [
    "AuditTrail",
]


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
