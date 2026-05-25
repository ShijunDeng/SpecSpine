from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "ReviewPacket",
]


@dataclass(frozen=True)
class ReviewPacket:
    root: Path
    feature_id: str | None
    changed_files: tuple[str, ...]
    validation: dict[str, Any]
    quality_gates: dict[str, Any]
    test_impact: dict[str, Any]
    review_checks: tuple[dict[str, Any], ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]
    feature: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "changed_files": list(self.changed_files),
            "feature_id": self.feature_id,
            "quality_gates": dict(self.quality_gates),
            "recommended_commands": list(self.recommended_commands),
            "review_checks": [dict(check) for check in self.review_checks],
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
            "test_impact": dict(self.test_impact),
            "validation": dict(self.validation),
        }
        if self.feature is not None:
            payload["feature"] = dict(self.feature)
        return payload
