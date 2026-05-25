from __future__ import annotations

from pathlib import Path

from .coverage import build_coverage_debt_report
from .health_models import (
    CoverageDebt,
)

__all__ = [
    "_build_coverage_debt_data",
]


def _build_coverage_debt_data(root: Path) -> CoverageDebt:
    try:
        report = build_coverage_debt_report(root)
    except OSError:
        return CoverageDebt(
            features_with_debt=0,
            missing_acceptance_criteria=0,
            covered_acceptance_criteria=0,
            acceptance_criteria_total=0,
            top_features_with_uncovered_ac=(),
        )

    features = report.get("features", [])
    debt_features = [
        f for f in features
        if f.get("coverage_required") and int(f.get("missing_acceptance_criteria", 0)) > 0
    ]
    top_features = tuple(
        {
            "feature_id": f["feature_id"],
            "missing": f["missing_acceptance_criteria"],
            "status": f["status"],
        }
        for f in sorted(debt_features, key=lambda x: -int(x["missing_acceptance_criteria"]))[:5]
    )

    return CoverageDebt(
        features_with_debt=report.get("features_with_debt", 0),
        missing_acceptance_criteria=report.get("missing_acceptance_criteria", 0),
        covered_acceptance_criteria=report.get("covered_acceptance_criteria", 0),
        acceptance_criteria_total=report.get("acceptance_criteria_total", 0),
        top_features_with_uncovered_ac=top_features,
    )
