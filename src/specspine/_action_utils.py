from __future__ import annotations

__all__ = [
    "_append_unique",
]


def _append_unique(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)
