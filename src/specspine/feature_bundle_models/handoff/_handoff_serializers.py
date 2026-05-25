from __future__ import annotations

from typing import Any

__all__ = [
    "serialize_items",
    "serialize_gaps",
]


def serialize_items(items: tuple[Any, ...]) -> list[dict[str, Any]]:
    return [item.as_dict() for item in items]


def serialize_gaps(gaps: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    return [dict(gap) for gap in gaps]
