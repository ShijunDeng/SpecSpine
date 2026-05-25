from __future__ import annotations

from pathlib import Path

__all__ = [
    "_relative_paths",
]


def _relative_paths(paths: list[Path], root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in paths)
