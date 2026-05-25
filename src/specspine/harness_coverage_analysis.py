from __future__ import annotations

from pathlib import Path

from .harness_coverage_models import (
    HarnessCoverageReport,
)
from .harness_coverage_aggregation import (
    _evaluate_single_feature_dimensions,
    _aggregate_workspace_dimensions,
)
from .harness_coverage_assembly import (
    _assemble_coverage_report,
)
from .harness_coverage_analysis_metrics import (
    _detect_blind_spots,
    _detect_redundancy,
    _generate_improvement_plan,
    _compute_maturity_score,
)
from .harness_coverage_baseline import (
    _load_baseline,
    _save_baseline,
    _compare_with_baseline,
)

__all__ = [
    "_detect_blind_spots",
    "_detect_redundancy",
    "_compute_maturity_score",
    "_generate_improvement_plan",
    "_load_baseline",
    "_save_baseline",
    "_compare_with_baseline",
    "build_harness_coverage_report",
]


def build_harness_coverage_report(
    root: Path,
    feature_filter: str | None = None,
) -> HarnessCoverageReport:
    resolved_root = root.expanduser().resolve()

    if feature_filter:
        dimensions, feature_id = _evaluate_single_feature_dimensions(
            feature_filter, resolved_root
        )
    else:
        dimensions, feature_id = _aggregate_workspace_dimensions(resolved_root)

    return _assemble_coverage_report(feature_id, dimensions, resolved_root)
