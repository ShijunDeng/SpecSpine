from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

RISK_BY_CATEGORY = {
    "config": "high",
    "feature-execution": "medium",
    "feature-quality": "medium",
    "feature-spec": "medium",
    "other": "low",
    "project-doc": "low",
    "source": "high",
    "test": "medium",
}


@dataclass(frozen=True)
class ChangeRiskReport:
    root: Path
    feature_id: str | None
    changed_files: tuple[str, ...]
    files: tuple[dict[str, Any], ...]
    feature_evidence: tuple[dict[str, Any], ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_files": list(self.changed_files),
            "feature_evidence": [dict(evidence) for evidence in self.feature_evidence],
            "feature_id": self.feature_id,
            "files": [dict(file) for file in self.files],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
        }


__all__ = [
    "RISK_BY_CATEGORY",
    "ChangeRiskReport",
]
