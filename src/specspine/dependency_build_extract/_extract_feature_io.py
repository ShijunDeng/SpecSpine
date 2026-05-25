"""Feature file I/O for dependency extraction."""

from __future__ import annotations

from pathlib import Path

from specspine.features import FEATURE_DIRECTORIES, FEATURE_FILE_PATHS

__all__ = [
    "_list_feature_slugs",
    "_read_all_feature_content",
]


def _list_feature_slugs(root: Path) -> list[str]:
    by_slug: dict[str, bool] = {}
    for directory_name in FEATURE_DIRECTORIES.values():
        directory = root / directory_name
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            by_slug[path.stem] = True
    return sorted(by_slug)


def _read_all_feature_content(root: Path, slug: str) -> str:
    parts: list[str] = []
    for kind in FEATURE_FILE_PATHS:
        file_path = root / FEATURE_FILE_PATHS[kind].format(slug=slug)
        if file_path.exists():
            parts.append(file_path.read_text(encoding="utf-8"))
    return "\n".join(parts)
