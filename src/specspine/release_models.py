from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

__all__ = [
    "_BREAKING_CHANGE_PATTERNS",
    "ReleaseEntry",
    "BreakingChange",
    "ReleaseNotesReport",
]

_BREAKING_CHANGE_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"removed\s+(?:the\s+)?`(--?\S+)`", re.IGNORECASE),
        "high",
        "CLI argument removed",
    ),
    (
        re.compile(r"removed\s+(?:the\s+)?required\s+field", re.IGNORECASE),
        "high",
        "Required field removed",
    ),
    (
        re.compile(r"changed\s+(?:the\s+)?(?:default|behavior|validation|output)", re.IGNORECASE),
        "medium",
        "Default behavior changed",
    ),
    (
        re.compile(r"deprecated\s+(?:the\s+)?`(--?\S+)`", re.IGNORECASE),
        "low",
        "Deprecation introduced",
    ),
    (
        re.compile(r"renamed\s+(?:the\s+)?`(--?\S+)`", re.IGNORECASE),
        "medium",
        "Name change",
    ),
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
