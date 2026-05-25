from __future__ import annotations

from .blueprint_models import (
    _AC_RE,
    _SHALL_RE,
)


def _extract_ac_ids(text: str) -> tuple[str, ...]:
    return tuple(sorted({m.group(0).upper() for m in _AC_RE.finditer(text)}))


def _has_shall(text: str) -> bool:
    return bool(_SHALL_RE.search(text))


__all__ = [
    "_extract_ac_ids",
    "_has_shall",
]
