from __future__ import annotations

__all__ = [
    "_dedupe_commands",
]


def _dedupe_commands(commands: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    for command in commands:
        if command in seen:
            continue
        seen.add(command)
        deduped.append(command)
    return tuple(deduped)
