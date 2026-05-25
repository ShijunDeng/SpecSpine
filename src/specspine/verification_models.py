from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VerificationMatrix:
    root: Path
    feature_id: str
    status: str
    ready: bool
    matrix: tuple[dict[str, Any], ...]
    evidence: dict[str, Any]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence": dict(self.evidence),
            "feature_id": self.feature_id,
            "matrix": [dict(row) for row in self.matrix],
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "status": self.status,
            "summary": dict(self.summary),
        }


__all__ = [
    "VerificationMatrix",
]
