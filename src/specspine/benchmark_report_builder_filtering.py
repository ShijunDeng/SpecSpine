from __future__ import annotations

from pathlib import Path

from .features import (
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)

__all__ = [
    "resolve_feature_slugs",
]


def resolve_feature_slugs(
    resolved_root: Path,
    feature_filter: str | None = None,
) -> list[str]:
    bundles = list_feature_bundles(resolved_root)
    slugs = [b["slug"] for b in bundles]

    if feature_filter:
        try:
            validate_feature_slug(feature_filter)
            if feature_filter in slugs:
                slugs = [feature_filter]
            else:
                slugs = []
        except InvalidFeatureSlug:
            slugs = []

    return slugs
