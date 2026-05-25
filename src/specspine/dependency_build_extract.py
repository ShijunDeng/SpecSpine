from __future__ import annotations

from pathlib import Path

from .dependency_models import EXPLICIT_DEP_PATTERNS
from .features import FEATURE_DIRECTORIES, FEATURE_FILE_PATHS


def _extract_slugs_from_text(text: str, current_slug: str, valid_slugs: set[str] | None = None) -> list[str]:
    slugs: list[str] = []
    for pattern in EXPLICIT_DEP_PATTERNS:
        for match in pattern.finditer(text):
            found = match.group(1)
            if found != current_slug and found not in slugs:
                if valid_slugs is None or found in valid_slugs:
                    slugs.append(found)
    return slugs


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


__all__ = [
    "_extract_shared_file_paths",
    "_extract_slugs_from_text",
    "_list_feature_slugs",
    "_read_all_feature_content",
]
