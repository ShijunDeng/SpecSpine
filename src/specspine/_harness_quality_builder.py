from __future__ import annotations

from pathlib import Path

from ._harness_quality_scorer import (
    HARNESS_DIMENSIONS,
    _compute_dimension_scores,
    _compute_harness_coverage,
)
from ._harness_sensor_collector import (
    _collect_sensors_for_feature,
    _collect_sensors_for_workspace,
)
from .harness_models import HarnessQualityReport

__all__ = [
    "build_harness_quality",
]


def build_harness_quality(root: Path, feature_id: str = "") -> HarnessQualityReport:
    resolved_root = root.expanduser().resolve()

    if feature_id:
        sensors = _collect_sensors_for_feature(feature_id, resolved_root)
    else:
        sensors = _collect_sensors_for_workspace(resolved_root)

    harness_coverage_pct = _compute_harness_coverage(sensors)
    dimension_scores = _compute_dimension_scores(sensors)
    resolved_feature_id = feature_id if feature_id else "workspace"

    return HarnessQualityReport(
        feature_id=resolved_feature_id,
        governed_dimensions=HARNESS_DIMENSIONS,
        sensor_count=len(sensors),
        harness_coverage_pct=harness_coverage_pct,
        dimension_scores=dimension_scores,
    )
