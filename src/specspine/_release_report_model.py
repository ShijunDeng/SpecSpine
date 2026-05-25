from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._release_entry_models import BreakingChange, ReleaseEntry

__all__ = [
    "ReleaseNotesReport",
]


@dataclass(frozen=True)
class ReleaseNotesReport:
    version: str
    date_range: str
    grouped_features: dict[str, list[ReleaseEntry]]
    breaking_changes: list[BreakingChange]
    summary: dict[str, Any]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for group_name, entries in self.grouped_features.items():
            grouped[group_name] = [entry.as_dict() for entry in entries]

        return {
            "breaking_changes": [bc.as_dict() for bc in self.breaking_changes],
            "date_range": self.date_range,
            "grouped_features": grouped,
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
            "version": self.version,
        }
