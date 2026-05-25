from __future__ import annotations

from pathlib import Path

__all__ = [
    "_relative_path",
    "_normalise_changed_file",
    "_read_text",
    "_candidate_files",
    "_area_prefixes",
]


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _normalise_changed_file(root: Path, value: str) -> str:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    return _relative_path(root, candidate.resolve())


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def _candidate_files(root: Path, globs: tuple[str, ...]) -> tuple[Path, ...]:
    files: list[Path] = []
    for pattern in globs:
        files.extend(path for path in root.glob(pattern) if path.is_file())
    return tuple(sorted(set(files)))


def _area_prefixes(area: str) -> tuple[str, ...]:
    if area == "implementation":
        return ("src/",)
    if area == "test":
        return ("tests/",)
    return ("docs/", "README.md", "AGENTS.md", "specs/", "execution/", "quality/")
