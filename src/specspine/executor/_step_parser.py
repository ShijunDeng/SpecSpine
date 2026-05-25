from __future__ import annotations

from pathlib import Path

from ..features import (
    FEATURE_FILE_PATHS,
    feature_bundle_paths,
)

from .executor_models import TASK_DEP_PATTERN

__all__ = [
    "_parse_task_dependencies",
    "_read_feature_contents",
]


def _parse_task_dependencies(text: str) -> list[str]:
    return TASK_DEP_PATTERN.findall(text)


def _read_feature_contents(root: Path, slug: str) -> dict[str, str]:
    paths = feature_bundle_paths(root, slug)
    contents: dict[str, str] = {}
    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
    return contents
