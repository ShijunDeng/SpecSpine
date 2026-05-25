from __future__ import annotations

from pathlib import Path

from .feature_bundle import FEATURE_FILE_PATHS
from .feature_bundle_io_paths import _relative_feature_paths
from .feature_status_helpers import _replace_or_insert_status_line

__all__ = [
    "_write_status_to_files",
]


def _write_status_to_files(
    paths: dict[str, Path],
    slug: str,
    status: str,
) -> tuple[str, ...]:
    updated_files: list[str] = []
    relative_paths = _relative_feature_paths(slug)

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8")
        path.write_text(_replace_or_insert_status_line(content, status), encoding="utf-8")
        updated_files.append(relative_paths[kind])

    return tuple(updated_files)
