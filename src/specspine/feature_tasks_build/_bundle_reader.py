from __future__ import annotations

from pathlib import Path

from ..feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    _relative_feature_paths,
    feature_bundle_paths,
    validate_feature_slug,
)

__all__ = [
    "_read_bundle_contents",
]


def _read_bundle_contents(
    root: Path,
    slug: str,
) -> tuple[dict[str, str], tuple[str, ...]]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents: dict[str, str] = {}
    missing_files: list[str] = []
    missing_paths: list[Path] = []

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
            continue

        missing_files.append(relative_path)
        missing_paths.append(path)

    if not contents:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(missing_paths),
        )

    return contents, tuple(missing_files)
