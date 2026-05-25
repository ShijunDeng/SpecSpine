from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ReadinessGates",
    "QualityGates",
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
