from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "RetrospectiveTheme",
]


@dataclass(frozen=True)
class RetrospectiveTheme:
    top_blocker_theme: str
    blocking_checks: dict[str, int]
    gaps: dict[str, int]
    coverage_states: dict[str, int]
    open_tasks: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "blocking_checks": dict(self.blocking_checks),
            "coverage_states": dict(self.coverage_states),
            "gaps": dict(self.gaps),
            "open_tasks": dict(self.open_tasks),
            "top_blocker_theme": self.top_blocker_theme,
        }
