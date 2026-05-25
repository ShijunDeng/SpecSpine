from __future__ import annotations

from pathlib import Path

from ..feature_bundle import (
    FEATURE_FILE_PATHS,
    _relative_feature_paths,
    feature_bundle_paths,
    validate_feature_slug,
    validate_feature_status,
)

__all__ = [
    "_validate_and_resolve",
]


def _validate_and_resolve(
    root: Path,
    slug: str,
    status: str,
) -> tuple[str, str, Path, dict[str, Path], dict[str, Path]]:
    slug = validate_feature_slug(slug)
    status = validate_feature_status(status)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)
    return slug, status, resolved_root, paths, relative_paths
