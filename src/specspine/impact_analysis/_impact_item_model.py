from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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


__all__ = [
    "ImpactItem",
]
