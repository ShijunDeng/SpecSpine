from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from pathlib import Path

from ._reports_feature_consistency import FeatureConsistency

__all__ = [
    "ConsistencyReport",
]


@dataclass(frozen=True)
class ConsistencyReport:
    root: Path
    feature_filter: str | None
    changed_files: tuple[str, ...]
    features: tuple[FeatureConsistency, ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_files": list(self.changed_files),
            "feature_filter": self.feature_filter,
            "features": [feature.as_dict() for feature in self.features],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
        }
