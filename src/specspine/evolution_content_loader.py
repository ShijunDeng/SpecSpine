from __future__ import annotations

from pathlib import Path

from .evolution_git import _build_versioned_content
from .features import FEATURE_FILE_PATHS

__all__ = [
    "load_feature_contents",
]


def load_feature_contents(
    resolved_root: Path,
    slug: str,
) -> tuple[dict[str, str | None], dict[str, str | None]]:
    base_contents = _build_versioned_content(resolved_root, slug)
    current_contents: dict[str, str | None] = {}
    for kind in FEATURE_FILE_PATHS:
        rel_path = FEATURE_FILE_PATHS[kind].format(slug=slug)
        file_path = resolved_root / rel_path
        if file_path.exists():
            current_contents[kind] = file_path.read_text(encoding="utf-8")
        else:
            current_contents[kind] = None
    return base_contents, current_contents
