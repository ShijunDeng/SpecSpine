from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "DriftEvent",
]


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
