from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "FeatureStatusTransitionError",
]


@dataclass(frozen=True)
class FeatureStatusTransitionError(ValueError):
    feature_id: str
    error: str
    transition: dict[str, object]
    message: str
    blocking_checks: tuple[dict[str, str], ...] = ()
    gaps: tuple[dict[str, str], ...] = ()
    missing_files: tuple[str, ...] = ()

    def __str__(self) -> str:
        return self.message

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "error": self.error,
            "feature_id": self.feature_id,
            "transition": dict(self.transition),
        }
        if self.blocking_checks:
            payload["blocking_checks"] = [dict(check) for check in self.blocking_checks]
        if self.gaps:
            payload["gaps"] = [dict(gap) for gap in self.gaps]
        if self.missing_files:
            payload["missing_files"] = list(self.missing_files)
        return payload
