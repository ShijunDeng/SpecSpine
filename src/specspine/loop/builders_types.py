from __future__ import annotations

from typing import Any, Callable

__all__ = [
    "StatusBuilder",
]

StatusBuilder = Callable[..., dict[str, Any]]
