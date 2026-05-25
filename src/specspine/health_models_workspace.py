from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "WorkspaceHealth",
    "FeaturePipeline",
]


@dataclass(frozen=True)
class WorkspaceHealth:
    complete: bool
    present: tuple[str, ...]
    missing: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "complete": self.complete,
            "missing": list(self.missing),
            "present": list(self.present),
        }


@dataclass(frozen=True)
class FeaturePipeline:
    features_total: int
    by_status: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "by_status": dict(self.by_status),
            "features_total": self.features_total,
        }
