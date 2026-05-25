from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "ConsistencyCheck",
    "ConsistencyReference",
]


@dataclass(frozen=True)
class ConsistencyReference:
    path: str
    line: int | None
    kind: str
    matched: str
    exists: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "exists": self.exists,
            "kind": self.kind,
            "line": self.line,
            "matched": self.matched,
            "path": self.path,
        }


@dataclass(frozen=True)
class ConsistencyCheck:
    id: str
    status: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "message": self.message,
            "status": self.status,
        }
