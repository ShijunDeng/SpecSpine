from __future__ import annotations

__all__ = [
    "EFFORT_VALUES",
    "DEFAULT_EFFORT",
    "_resolve_effort",
]

EFFORT_VALUES = {"S": 1, "M": 2, "L": 4, "XL": 8}
DEFAULT_EFFORT = 3


def _resolve_effort(effort: str) -> int:
    return EFFORT_VALUES.get(effort, DEFAULT_EFFORT)
