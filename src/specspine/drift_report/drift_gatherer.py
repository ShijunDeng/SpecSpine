from __future__ import annotations

from pathlib import Path
from typing import Any

from ._gatherer_loader import _load_feature_records
from ._gatherer_stats import _compute_severity_distribution, _compute_summary
from ._gatherer_trends import _compute_trends, _compute_scan_metadata
from ..drift_models import FeatureDriftRecord

__all__ = [
    "_gather_feature_drift_records",
]


def _gather_feature_drift_records(
    resolved_root: Path,
    *,
    feature_filter: str | None = None,
    baseline: str | None = None,
    since: str | None = None,
) -> tuple[tuple[FeatureDriftRecord, ...], dict[str, Any], dict[str, Any], tuple[dict[str, Any], ...]]:
    feature_tuple, metadata = _load_feature_records(
        resolved_root,
        feature_filter=feature_filter,
        baseline=baseline,
        since=since,
    )

    severity_dist = _compute_severity_distribution(feature_tuple)
    summary = _compute_summary(feature_tuple, severity_dist)
    trends = _compute_trends(feature_tuple, since)
    scan_metadata = _compute_scan_metadata(resolved_root, metadata)

    return feature_tuple, summary, scan_metadata, trends
