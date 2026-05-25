from __future__ import annotations

__all__ = [
    "_replace_slug_local",
]


def _replace_slug_local(commands, slug: str) -> tuple[str, ...]:
    return tuple(command.replace("<slug>", slug) for command in commands)
