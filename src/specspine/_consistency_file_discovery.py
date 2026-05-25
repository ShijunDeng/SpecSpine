from __future__ import annotations

from pathlib import Path

from .consistency_references import (
    _explicit_paths_from_feature_files,
    _feature_missing_files,
    _feature_source_files,
)

__all__ = [
    "_discover_feature_files",
]


def _discover_feature_files(
    root: Path,
    slug: str,
) -> dict[str, list[str]]:
    source_files = _feature_source_files(root, slug)
    missing_files = _feature_missing_files(root, slug)
    explicit_paths = _explicit_paths_from_feature_files(root, source_files)
    return {
        "source_files": source_files,
        "missing_files": missing_files,
        "explicit_paths": explicit_paths,
    }
