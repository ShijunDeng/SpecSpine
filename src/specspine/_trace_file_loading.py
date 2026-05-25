from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    feature_bundle_paths,
    _relative_feature_paths,
)

__all__ = [
    "_load_feature_contents",
]


def _load_feature_contents(
    resolved_root: Path,
    slug: str,
) -> tuple[dict[str, str], list[str], dict[str, dict[str, object]]]:
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents: dict[str, str] = {}
    missing_files: list[str] = []
    missing_paths: list[Path] = []
    sources: dict[str, dict[str, object]] = {}

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        exists = path.exists()
        sources[kind] = {
            "exists": exists,
            "path": relative_path,
        }
        if exists:
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

    return contents, missing_files, sources
