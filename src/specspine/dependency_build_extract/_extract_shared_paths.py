"""Extract shared file paths between two features."""

from __future__ import annotations

from pathlib import Path

from specspine.features import FEATURE_FILE_PATHS

__all__ = [
    "_extract_shared_file_paths",
]


def _extract_shared_file_paths(root: Path, slug_a: str, slug_b: str) -> list[str]:
    paths_a: set[str] = set()
    paths_b: set[str] = set()
    for kind in FEATURE_FILE_PATHS:
        file_path = root / FEATURE_FILE_PATHS[kind].format(slug=slug_a)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    paths_a.add(stripped.lower())

        file_path = root / FEATURE_FILE_PATHS[kind].format(slug=slug_b)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    paths_b.add(stripped.lower())

    shared = sorted(paths_a & paths_b)
    return [p for p in shared if len(p) > 3]
