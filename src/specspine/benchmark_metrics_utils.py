from __future__ import annotations

import re
from pathlib import Path

__all__ = [
    "_read_text",
    "_count_pattern",
]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _count_pattern(content: str, pattern: re.Pattern[str]) -> int:
    return len(pattern.findall(content))
