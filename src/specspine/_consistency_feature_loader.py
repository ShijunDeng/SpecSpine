from __future__ import annotations

from pathlib import Path

from .consistency_records import (
    _build_feature_record,
    _missing_feature_record,
)
from .consistency_utils import (
    _dedupe,
    _normalise_changed_file,
)
from .features import (
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)

__all__ = [
    "_load_feature_consistency_records",
    "_resolve_and_validate_slug",
]


def _resolve_and_validate_slug(slug: str | None) -> str | None:
    if slug is not None:
        return validate_feature_slug(slug)
    return slug


def _load_feature_consistency_records(
    resolved_root: Path,
    feature_filter: str | None,
    changed_files: tuple[str, ...],
) -> tuple:
    normalised_changed_files = tuple(
        _dedupe(
            [
                _normalise_changed_file(resolved_root, changed_file)
                for changed_file in changed_files
            ]
        )
    )

    discovered = list_feature_bundles(resolved_root)
    discovered_slugs = tuple(str(feature["slug"]) for feature in discovered)
    if feature_filter is not None:
        slugs = (feature_filter,)
    else:
        slugs = discovered_slugs

    from .consistency_models import FeatureConsistency

    features: list[FeatureConsistency] = []
    for slug in slugs:
        validate_feature_slug(slug)
        if slug not in discovered_slugs:
            features.append(_missing_feature_record(resolved_root, slug))
        else:
            features.append(
                _build_feature_record(
                    resolved_root,
                    slug,
                    changed_files=normalised_changed_files,
                )
            )

    feature_tuple = tuple(sorted(features, key=lambda feature: feature.feature_id))
    return feature_tuple, normalised_changed_files, len(discovered)
