from __future__ import annotations

from pathlib import Path
from typing import Any

from .coverage_plan_items import _missing_feature_plan_report
from .features import (
    list_feature_bundles,
    validate_feature_slug,
)

__all__ = [
    "resolve_coverage_plan_features",
]


def resolve_coverage_plan_features(
    root: Path,
    *,
    feature_filter: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    resolved_root = root.expanduser().resolve()
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)

    features = list_feature_bundles(resolved_root)
    if feature_filter is not None:
        features = [
            feature for feature in features if str(feature["slug"]) == feature_filter
        ]

    return features, feature_filter
