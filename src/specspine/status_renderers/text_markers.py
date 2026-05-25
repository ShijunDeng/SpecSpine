from __future__ import annotations

__all__ = [
    "_complete_marker",
    "_marker",
]


def _marker(value: bool) -> str:
    return "ok" if value else "missing"


def _complete_marker(value: bool) -> str:
    return "complete" if value else "incomplete"
