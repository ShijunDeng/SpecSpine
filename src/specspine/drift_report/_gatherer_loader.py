from __future__ import annotations

from pathlib import Path
from typing import Any

from ..drift_analysis import _correlate_cross_feature_drift, _parse_feature_drift
from ..drift_models import FeatureDriftRecord
from ..features import (
    list_feature_bundles,
    validate_feature_slug,
)

__all__ = [
    "_load_feature_records",
]


def _load_feature_records(
    resolved_root: Path,
    *,
    feature_filter: str | None = None,
    baseline: str | None = None,
    since: str | None = None,
) -> tuple[tuple[FeatureDriftRecord, ...], dict[str, Any]]:
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)

    discovered = list_feature_bundles(resolved_root)
    discovered_slugs = {str(f["slug"]) for f in discovered}

    if feature_filter is not None:
        slugs = (feature_filter,)
    else:
        slugs = tuple(sorted(discovered_slugs))

    feature_records: list[FeatureDriftRecord] = []
    for slug in slugs:
        record = _parse_feature_drift(slug, resolved_root, baseline, since)
        feature_records.append(record)

    _correlate_cross_feature_drift(feature_records, resolved_root)

    feature_tuple = tuple(sorted(feature_records, key=lambda f: f.feature_id))

    metadata = {
        "baseline": baseline,
        "since": since,
    }

    return feature_tuple, metadata
