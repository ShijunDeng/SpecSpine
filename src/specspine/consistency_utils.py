from __future__ import annotations

from pathlib import Path

from .consistency_models import ConsistencyReference

__all__ = [
    "_area_prefixes",
    "_candidate_files",
    "_dedupe",
    "_dedupe_references",
    "_normalise_changed_file",
    "_read_text",
    "_relative_path",
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


def _dedupe(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        deduped.append(value)
        seen.add(value)
    return tuple(deduped)


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


def _dedupe_references(
    references: list[ConsistencyReference],
) -> tuple[ConsistencyReference, ...]:
    seen: set[tuple[str, int | None, str, str]] = set()
    deduped: list[ConsistencyReference] = []
    for reference in references:
        key = (reference.path, reference.line, reference.kind, reference.matched)
        if key in seen:
            continue
        deduped.append(reference)
        seen.add(key)
    return tuple(sorted(deduped, key=lambda item: (item.path, item.line or 0, item.kind)))
