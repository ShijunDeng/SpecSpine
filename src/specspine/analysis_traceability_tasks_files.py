from __future__ import annotations

from .features import (
    FEATURE_FILE_PATHS,
)

__all__ = [
    "_source_files",
    "_missing_files",
]


def _source_files(feature: dict[str, object], slug: str) -> tuple[str, ...]:
    files = feature.get("files")
    if isinstance(files, dict):
        return tuple(sorted(str(path) for path in files.values()))
    return tuple(
        relative_path.format(slug=slug)
        for relative_path in FEATURE_FILE_PATHS.values()
    )


def _missing_files(feature: dict[str, object], slug: str) -> tuple[str, ...]:
    missing = feature.get("missing_files")
    if isinstance(missing, list):
        return tuple(sorted(str(path) for path in missing))
    return tuple(
        relative_path.format(slug=slug)
        for relative_path in FEATURE_FILE_PATHS.values()
    )
