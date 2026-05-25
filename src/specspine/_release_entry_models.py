from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "ReleaseEntry",
    "BreakingChange",
]


@dataclass(frozen=True)
class ReleaseEntry:
    slug: str
    title: str
    priority: str
    status_transition: str
    ac_summary: str
    validation_evidence_count: int
    project: str
    effort: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "ac_summary": self.ac_summary,
            "effort": self.effort,
            "priority": self.priority,
            "project": self.project,
            "slug": self.slug,
            "status_transition": self.status_transition,
            "title": self.title,
            "validation_evidence_count": self.validation_evidence_count,
        }


@dataclass(frozen=True)
class BreakingChange:
    feature_id: str
    description: str
    severity: str
    affected_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "affected_commands": list(self.affected_commands),
            "description": self.description,
            "feature_id": self.feature_id,
            "severity": self.severity,
        }
