from __future__ import annotations

from pathlib import Path


def _gather_status_data(
    resolved_root: Path,
    slug: str,
) -> tuple:
    from ...feature_bundle import (
        _relative_feature_paths,
        feature_bundle_paths,
        get_feature_status,
        validate_feature_slug,
    )
    slug = validate_feature_slug(slug)
    relative_paths = _relative_feature_paths(slug)
    status_report = get_feature_status(resolved_root, slug)
    return relative_paths, status_report


__all__ = [
    "_gather_status_data",
]
