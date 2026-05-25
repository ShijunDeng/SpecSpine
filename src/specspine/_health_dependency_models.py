from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DependencyHealth",
    "SecuritySummary",
]


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
