from __future__ import annotations

from pathlib import Path

__all__ = [
    "_relative_path",
    "_normalise_changed_file",
    "_is_within_root",
]


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _normalise_changed_file(root: Path, value: str) -> tuple[str, Path]:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    return _relative_path(root, resolved), resolved


def _is_within_root(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
