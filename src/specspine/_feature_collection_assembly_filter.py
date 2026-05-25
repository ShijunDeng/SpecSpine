from __future__ import annotations

from pathlib import Path

from .features import (
    InvalidFeatureSlug,
    list_feature_bundles,
    read_feature_metadata,
)

__all__ = [
    "_iter_validated_features",
]


def _iter_validated_features(resolved_root: Path):
    feature_bundles = list_feature_bundles(resolved_root)
    for feature in feature_bundles:
        status = feature.get("status")
        if status not in ("validated", "archived"):
            continue
        slug = str(feature["slug"])
        try:
            metadata = read_feature_metadata(resolved_root, slug)
        except InvalidFeatureSlug:
            continue
        yield slug, status, metadata
