from __future__ import annotations

from pathlib import Path
from typing import Any


def _read_top_level_scalars(path: Path) -> dict[str, Any]:
    from ..status import _clean_scalar
    if not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    values: dict[str, Any] = {}
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent != 0 or ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        value = value.strip()
        if value:
            values[key.strip()] = _clean_scalar(value)

    return values


__all__ = [
    "_read_top_level_scalars",
]
