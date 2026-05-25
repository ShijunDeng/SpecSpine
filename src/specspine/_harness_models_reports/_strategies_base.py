from __future__ import annotations

__all__ = [
    "_FrozenBase",
]


class _FrozenBase:
    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("frozen instance")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("frozen instance")
