from __future__ import annotations

from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    list_feature_bundles,
    validate_feature_slug,
)

__all__ = [
    "resolve_feature_filter",
    "discover_and_select_features",
]


def resolve_feature_filter(feature_filter: str | None) -> str | None:
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)
    return feature_filter


def discover_and_select_features(
    resolved_root: Path,
    feature_filter: str | None,
) -> list[dict]:
    discovered = list_feature_bundles(resolved_root)
    selected = [
        feature
        for feature in discovered
        if feature_filter is None or str(feature["slug"]) == feature_filter
    ]
    if feature_filter is not None and not selected:
        selected = [
            {
                "slug": feature_filter,
                "complete": False,
                "files": {},
                "status": None,
                "status_consistent": False,
                "missing_files": [
                    relative_path.format(slug=feature_filter)
                    for relative_path in FEATURE_FILE_PATHS.values()
                ],
            }
        ]
    return selected
