from __future__ import annotations

from typing import Any

__all__ = [
    "_recommended_commands",
]


def _recommended_commands(
    status: dict[str, Any],
    validation_commands: list[dict[str, object]],
) -> list[str]:
    commands: list[str] = []
    for recommendation in status.get("recommendations", []):
        if isinstance(recommendation, str) and recommendation not in commands:
            commands.append(recommendation)
    readiness = status.get("readiness_summary", {})
    if isinstance(readiness, dict):
        for command in readiness.get("recommended_commands", []):
            if isinstance(command, str) and command not in commands:
                commands.append(command)
    for command in validation_commands:
        value = str(command["command"])
        if value not in commands:
            commands.append(value)
    if "specspine loop packet . --json" not in commands:
        commands.append("specspine loop packet . --json")
    return commands
