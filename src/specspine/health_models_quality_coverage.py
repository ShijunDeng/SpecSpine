from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "CoverageDebt",
]


@dataclass(frozen=True)
class CoverageDebt:
    features_with_debt: int
    missing_acceptance_criteria: int
    covered_acceptance_criteria: int
    acceptance_criteria_total: int
    top_features_with_uncovered_ac: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "acceptance_criteria_total": self.acceptance_criteria_total,
            "covered_acceptance_criteria": self.covered_acceptance_criteria,
            "features_with_debt": self.features_with_debt,
            "missing_acceptance_criteria": self.missing_acceptance_criteria,
            "top_features_with_uncovered_ac": list(self.top_features_with_uncovered_ac),
        }
