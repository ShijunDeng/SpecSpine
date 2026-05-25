from __future__ import annotations

from pathlib import Path

from .features import FEATURE_FILE_PATHS
from .evolution_git_helpers import _run_git

__all__ = [
    "_build_versioned_content",
]


def _build_versioned_content(
    root: Path,
    slug: str,
    base: str | None = None,
) -> dict[str, str | None]:
    contents: dict[str, str | None] = {}
    for kind in FEATURE_FILE_PATHS:
        rel_path = FEATURE_FILE_PATHS[kind].format(slug=slug)
        file_path = root / rel_path
        if not file_path.exists():
            contents[kind] = None
            continue

        if base is None:
            contents[kind] = file_path.read_text(encoding="utf-8")
        else:
            result = _run_git(
                ["show", f"{base}:{rel_path}"],
                root,
            )
            if result.returncode == 0:
                contents[kind] = result.stdout
            else:
                contents[kind] = None
    return contents
