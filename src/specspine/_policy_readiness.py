from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .features import FEATURE_PRIORITIES, FEATURE_STATUSES, FeatureMetadata

__all__ = [
    "ReadinessCoveragePolicy",
]


@dataclass(frozen=True)
class ReadinessCoveragePolicy:
    enabled: bool = False
    default: bool = False
    priorities: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    feature_ids: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def requires_coverage(
        self,
        *,
        feature_id: str,
        metadata: FeatureMetadata,
        status: str,
    ) -> bool:
        if not self.enabled:
            return False
        return (
            self.default
            or feature_id in self.feature_ids
            or metadata.priority in self.priorities
            or status in self.statuses
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "default": self.default,
            "enabled": self.enabled,
            "feature_ids": list(self.feature_ids),
            "priorities": list(self.priorities),
            "statuses": list(self.statuses),
            "warnings": list(self.warnings),
        }
