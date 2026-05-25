from __future__ import annotations

from typing import Any

__all__ = [
    "render_lifecycle_steps",
    "render_subagents",
    "render_safety_notes",
    "render_upstreams",
]


def render_lifecycle_steps(packet: dict[str, Any]) -> list[str]:
    lines = ["", "## Lifecycle Steps"]
    for step in packet["lifecycle_steps"]:
        lines.append(f"- {step['status']}")
        for command in step["commands"]:
            lines.append(f"  - `{command['command']}`")
    return lines


def render_subagents(packet: dict[str, Any]) -> list[str]:
    lines = ["", "## Subagents"]
    for subagent in packet["subagents"]:
        lines.append(f"- {subagent['id']}: {subagent['focus']}")
    return lines


def render_safety_notes(packet: dict[str, Any]) -> list[str]:
    lines = ["", "## Safety Notes"]
    for note in packet["safety_notes"]:
        lines.append(f"- {note}")
    return lines


def render_upstreams(packet: dict[str, Any]) -> list[str]:
    lines = ["", "## Upstreams"]
    upstreams = packet["upstreams"]
    if upstreams:
        for key in sorted(upstreams):
            upstream = upstreams[key]
            enabled = "enabled" if upstream.get("enabled") else "disabled"
            config = upstream.get("config", "")
            lines.append(f"- {key}: {enabled}, config={config}")
    else:
        lines.append("- none")
    return lines
