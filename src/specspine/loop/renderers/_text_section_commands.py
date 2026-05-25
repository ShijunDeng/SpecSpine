from __future__ import annotations

from typing import Any

__all__ = [
    "render_context_commands",
    "render_validation_commands",
    "render_recommended_commands",
]


def render_context_commands(packet: dict[str, Any]) -> list[str]:
    lines = ["", "## Context Commands"]
    for command in packet["context_commands"]:
        lines.append(f"- {command['id']}: `{command['command']}`")
    return lines


def render_validation_commands(packet: dict[str, Any]) -> list[str]:
    lines = ["", "## Validation Commands"]
    for command in packet["validation_commands"]:
        lines.append(f"- {command['id']}: `{command['command']}`")
    return lines


def render_recommended_commands(packet: dict[str, Any]) -> list[str]:
    lines = ["", "## Recommended Commands"]
    for command in packet["recommended_commands"]:
        lines.append(f"- `{command}`")
    return lines
