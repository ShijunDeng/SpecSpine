from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "HygieneFinding",
]


@dataclass(frozen=True)
class HygieneFinding:
    id: str
    severity: str
    category: str
    path: str
    message: str
    source: str
    line: int | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "category": self.category,
            "id": self.id,
            "message": self.message,
            "path": self.path,
            "severity": self.severity,
            "source": self.source,
        }
        if self.line is not None:
            payload["line"] = self.line
        return payload
