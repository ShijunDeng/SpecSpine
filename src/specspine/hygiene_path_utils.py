from __future__ import annotations

from pathlib import Path

__all__ = [
    "_relative_path",
    "_display_directory",
    "_normalise_changed_file",
    "_dedupe",
]


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _display_directory(path: str) -> str:
    return path if path.endswith("/") else path + "/"


def _normalise_changed_file(root: Path, value: str) -> str:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    return _relative_path(root, candidate.resolve())


def _dedupe(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        deduped.append(value)
        seen.add(value)
    return tuple(deduped)
