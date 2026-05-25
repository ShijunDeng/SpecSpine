from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "ProvenanceManifest",
]


@dataclass(frozen=True)
class ProvenanceManifest:
    root: Path
    feature_id: str | None
    artifacts: tuple[dict[str, Any], ...]
    feature_evidence: tuple[dict[str, Any], ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "artifacts": [dict(artifact) for artifact in self.artifacts],
            "feature_evidence": [
                dict(evidence) for evidence in self.feature_evidence
            ],
            "feature_id": self.feature_id,
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
        }
