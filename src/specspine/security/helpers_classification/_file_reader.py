from __future__ import annotations

from pathlib import Path

__all__ = [
    "MAX_TEXT_BYTES",
    "_read_small_text",
]

MAX_TEXT_BYTES = 128 * 1024


def _read_small_text(path: Path) -> tuple[str | None, str | None]:
    try:
        stat = path.stat()
    except OSError as error:
        return None, f"stat_error:{error.__class__.__name__}"
    if not path.is_file():
        return None, "not_file"
    if stat.st_size > MAX_TEXT_BYTES:
        return None, "too_large"
    try:
        raw = path.read_bytes()
    except OSError as error:
        return None, f"read_error:{error.__class__.__name__}"
    if b"\0" in raw:
        return None, "binary"
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        try:
            return raw.decode("utf-8", errors="replace"), None
        except UnicodeDecodeError:
            return None, "decode_error"
