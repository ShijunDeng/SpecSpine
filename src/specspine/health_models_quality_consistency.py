from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "ConsistencyDrift",
]


@dataclass(frozen=True)
class ConsistencyDrift:
    features_scanned: int
    checks_pass: int
    checks_fail: int
    checks_warn: int
    checks_total: int
    top_failing_features: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "checks_fail": self.checks_fail,
            "checks_pass": self.checks_pass,
            "checks_total": self.checks_total,
            "checks_warn": self.checks_warn,
            "features_scanned": self.features_scanned,
            "top_failing_features": list(self.top_failing_features),
        }
