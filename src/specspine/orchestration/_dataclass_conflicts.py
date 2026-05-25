from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "OrchestrationConflict",
]


@dataclass(frozen=True)
class OrchestrationConflict:
    conflict_type: str
    affected_files: tuple[str, ...]
    affected_ac_ids: tuple[str, ...]
    features_involved: tuple[str, ...]
    severity: str
    description: str

    def as_dict(self) -> dict[str, object]:
        return {
            "affected_ac_ids": list(self.affected_ac_ids),
            "affected_files": list(self.affected_files),
            "conflict_type": self.conflict_type,
            "description": self.description,
            "features_involved": list(self.features_involved),
            "severity": self.severity,
        }
