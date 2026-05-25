from __future__ import annotations

from pathlib import Path

from .feature_bundle import FeatureStatusReport
from ._path_utils import _collect_paths, _raise_missing_bundle_error

__all__ = [
    "_validate_status_preconditions",
]


def _validate_status_preconditions(
    resolved_root: Path,
    slug: str,
    status: str,
    enforce_transition: bool,
) -> tuple[FeatureStatusReport, list[Path]]:
    from .feature_bundle import get_feature_status
    before = get_feature_status(resolved_root, slug)
    existing_paths = [path for path in _collect_paths(resolved_root, slug).values() if path.exists()]
    if not existing_paths:
        _raise_missing_bundle_error(slug, status, enforce_transition, before)
    return before, existing_paths
