from __future__ import annotations

from pathlib import Path

from .feature_bundle_models import FEATURE_FILE_PATHS
from .feature_bundle_validation import validate_feature_slug

__all__ = [
    "feature_bundle_paths",
    "_relative_feature_paths",
    "get_feature_files",
    "_path_as_posix",
    "_sync_body_source",
]


def feature_bundle_paths(root: Path, slug: str) -> dict[str, Path]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    return {
        kind: resolved_root / relative_path.format(slug=slug)
        for kind, relative_path in FEATURE_FILE_PATHS.items()
    }


def _relative_feature_paths(slug: str) -> dict[str, str]:
    return {
        kind: relative_path.format(slug=slug)
        for kind, relative_path in FEATURE_FILE_PATHS.items()
    }


def get_feature_files(root: Path, slug: str) -> dict[str, Path]:
    return feature_bundle_paths(root, slug)


def _path_as_posix(path: Path) -> str:
    return path.as_posix()


def _sync_body_source(slug: str, filename: str) -> str:
    return str(Path(".specspine") / "sync-plan" / slug / filename)
