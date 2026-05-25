from __future__ import annotations

from typing import Any

__all__ = [
    "_dedupe_commands",
    "_review_check",
]


def _dedupe_commands(*command_groups: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    commands: list[str] = []
    seen: set[str] = set()
    for group in command_groups:
        for command in group:
            if command not in seen:
                commands.append(command)
                seen.add(command)
    return tuple(commands)


def _review_check(check_id: str, passed: bool, message: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "message": message,
        "status": "pass" if passed else "fail",
    }
