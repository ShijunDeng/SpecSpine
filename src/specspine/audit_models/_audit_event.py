from __future__ import annotations

from typing import Any

__all__ = [
    "AuditEvent",
]


from dataclasses import dataclass


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
