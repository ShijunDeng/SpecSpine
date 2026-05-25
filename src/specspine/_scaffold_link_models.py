from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScaffoldCoverageLink:
    ac_id: str
    target_path: str
    class_name: str
    method_name: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "target_path": self.target_path,
        }


@dataclass(frozen=True)
class ScaffoldSkippedCriterion:
    ac_id: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "reason": self.reason,
        }


__all__ = [
    "ScaffoldCoverageLink",
    "ScaffoldSkippedCriterion",
]
