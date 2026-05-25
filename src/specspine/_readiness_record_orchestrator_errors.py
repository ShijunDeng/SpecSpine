from __future__ import annotations

from typing import Any

__all__ = [
    "_is_error_record",
]


def _is_error_record(result: Any) -> bool:
    return isinstance(result, dict) and "reason" in result
