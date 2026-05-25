from __future__ import annotations

from pathlib import Path
from typing import Any

from ..feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    feature_bundle_paths,
    validate_feature_slug,
)


def load_feature_contents(
    root: Path,
    slug: str,
) -> tuple[Path, dict[str, str], list[str], list[str]]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = {
        kind: relative_path.format(slug=slug)
        for kind, relative_path in FEATURE_FILE_PATHS.items()
    }

    contents: dict[str, str] = {}
    source_files: list[str] = []
    missing_files: list[str] = []
    missing_paths: list[Path] = []

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
            source_files.append(relative_path)
            continue

        missing_files.append(relative_path)
        missing_paths.append(path)

    if not contents:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(missing_paths),
        )

    return resolved_root, contents, source_files, missing_files


__all__ = [
    "load_feature_contents",
]
