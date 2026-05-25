from __future__ import annotations

from pathlib import Path

from .hygiene_models import (
    GENERATED_FILE_NAMES,
    GENERATED_FILE_SUFFIXES,
)

__all__ = [
    "_generated_file_source",
    "_read_text",
]


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
