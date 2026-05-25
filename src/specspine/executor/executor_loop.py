from __future__ import annotations

from ._loop_runner import run_execution_loop

__all__ = [
    "run_execution_loop",
]


def __getattr__(name: str) -> object:
    if name in __all__:
        from ._loop_runner import run_execution_loop as _func
        return _func
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
