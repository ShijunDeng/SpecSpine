from __future__ import annotations

from pathlib import Path

from .hygiene_models import (
    GENERATED_FILE_NAMES,
    GENERATED_FILE_SUFFIXES,
    HygieneFinding,
)

__all__ = [
    "_relative_path",
    "_display_directory",
    "_normalise_changed_file",
    "_dedupe",
    "_generated_file_source",
    "_read_text",
    "_add_finding",
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


def _generated_file_source(path: Path) -> str | None:
    if path.name in GENERATED_FILE_NAMES:
        return path.name
    for suffix in GENERATED_FILE_SUFFIXES:
        if path.name.endswith(suffix):
            return "*" + suffix
    return None


def _read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        return None, "read_error:" + error.__class__.__name__
    if b"\0" in raw:
        return None, "binary"
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        return None, "decode_error"


def _add_finding(
    findings: list[HygieneFinding],
    *,
    finding_id: str,
    severity: str,
    category: str,
    path: str,
    message: str,
    source: str,
    line: int | None = None,
) -> None:
    findings.append(
        HygieneFinding(
            id=finding_id,
            severity=severity,
            category=category,
            path=path,
            line=line,
            message=message,
            source=source,
        )
    )
