from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ReadinessGates",
    "QualityGates",
    "DependencyHealth",
    "SecuritySummary",
]


@dataclass(frozen=True)
class ReadinessGates:
    features_total: int
    ready: int
    not_ready: int
    blocking_checks_total: int
    gaps_total: int
    top_blockers: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "blocking_checks_total": self.blocking_checks_total,
            "features_total": self.features_total,
            "gaps_total": self.gaps_total,
            "not_ready": self.not_ready,
            "ready": self.ready,
            "top_blockers": list(self.top_blockers),
        }


@dataclass(frozen=True)
class QualityGates:
    required_total: int
    required_done: int
    required_open: int
    definition_total: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "definition_total": self.definition_total,
            "required_done": self.required_done,
            "required_open": self.required_open,
            "required_total": self.required_total,
        }


@dataclass(frozen=True)
class DependencyHealth:
    features_total: int
    cycles: list[list[str]]
    critical_path: list[str]
    critical_path_effort: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "critical_path": self.critical_path,
            "critical_path_effort": self.critical_path_effort,
            "cycles": self.cycles,
            "features_total": self.features_total,
        }


@dataclass(frozen=True)
class SecuritySummary:
    cues_total: int
    high: int
    medium: int
    low: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "cues_total": self.cues_total,
            "high": self.high,
            "low": self.low,
            "medium": self.medium,
        }
