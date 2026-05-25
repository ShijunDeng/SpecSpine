from __future__ import annotations

from pathlib import Path
from typing import Any

from .harness_coverage_models import HarnessCoverageReport
from .harness_coverage_analysis_metrics import (
    _detect_blind_spots,
    _generate_improvement_plan,
    _compute_maturity_score,
)
from .harness_coverage_baseline import (
    _load_baseline,
    _compare_with_baseline,
)

__all__ = [
    "_assemble_coverage_report",
]


def _assemble_coverage_report(
    feature_id: str,
    dimensions: list,
    resolved_root: Path,
) -> HarnessCoverageReport:
    blind_spots = _detect_blind_spots(dimensions)
    improvement_plan = _generate_improvement_plan(dimensions, blind_spots)
    maturity_score = _compute_maturity_score(dimensions)

    baseline = _load_baseline(resolved_root)
    baseline_comparison: dict[str, Any] = {}
    if baseline is not None:
        baseline_comparison = _compare_with_baseline(
            HarnessCoverageReport(
                feature_id=feature_id,
                dimensions=tuple(dimensions),
                maturity_score=maturity_score,
                blind_spots=tuple(blind_spots),
                improvement_plan=tuple(improvement_plan),
            ),
            baseline,
        )

    safety_notes = (
        "This harness coverage report is advisory local evidence.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )

    return HarnessCoverageReport(
        feature_id=feature_id,
        dimensions=tuple(dimensions),
        maturity_score=maturity_score,
        blind_spots=tuple(blind_spots),
        improvement_plan=tuple(improvement_plan),
        baseline_comparison=baseline_comparison,
        safety_notes=safety_notes,
    )
