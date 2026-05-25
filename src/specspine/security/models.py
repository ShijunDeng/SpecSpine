from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "SecurityCueReport",
]


@dataclass(frozen=True)
class SecurityCueReport:
    root: Path
    feature_id: str | None
    changed_files: tuple[str, ...]
    files: tuple[dict[str, Any], ...]
    cues: tuple[dict[str, Any], ...]
    feature_evidence: tuple[dict[str, Any], ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_files": list(self.changed_files),
            "cues": [dict(cue) for cue in self.cues],
            "feature_evidence": [dict(evidence) for evidence in self.feature_evidence],
            "feature_id": self.feature_id,
            "files": [dict(file) for file in self.files],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
        }
