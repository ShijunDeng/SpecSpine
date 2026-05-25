from __future__ import annotations

from typing import Any

__all__ = [
    "render_loop_packet_text",
]


def render_loop_packet_text(packet: dict[str, Any]) -> str:
    lines = [
        "# SpecSpine Agent Loop Packet",
        "",
        f"Root: {packet['root']}",
        f"Deadline: {packet['deadline'] or 'none'}",
        "",
        "## Summary",
    ]
    summary = packet["summary"]
    for key in (
        "features_total",
        "features_ready",
        "features_not_ready",
        "tasks_open_total",
        "gaps_total",
        "blocking_checks_total",
        "enabled_upstreams",
    ):
        lines.append(f"- {key}: {summary[key]}")

    lines.extend(["", "## Core Features"])
    core_features = packet["core_features"]
    if core_features:
        for feature in core_features:
            lines.append(
                "- "
                f"{feature['slug']} "
                f"status={feature['status']} "
                f"ready={'yes' if feature['ready'] else 'no'} "
                f"tasks_open={feature['tasks_summary'].get('open', 0)} "
                f"gaps={feature['gaps']} "
                f"blocking={feature['blocking_checks']}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Context Commands"])
    for command in packet["context_commands"]:
        lines.append(f"- {command['id']}: `{command['command']}`")

    lines.extend(["", "## Lifecycle Steps"])
    for step in packet["lifecycle_steps"]:
        lines.append(f"- {step['status']}")
        for command in step["commands"]:
            lines.append(f"  - `{command['command']}`")

    lines.extend(["", "## Subagents"])
    for subagent in packet["subagents"]:
        lines.append(f"- {subagent['id']}: {subagent['focus']}")

    lines.extend(["", "## Validation Commands"])
    for command in packet["validation_commands"]:
        lines.append(f"- {command['id']}: `{command['command']}`")

    lines.extend(["", "## Safety Notes"])
    for note in packet["safety_notes"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Upstreams"])
    upstreams = packet["upstreams"]
    if upstreams:
        for key in sorted(upstreams):
            upstream = upstreams[key]
            enabled = "enabled" if upstream.get("enabled") else "disabled"
            config = upstream.get("config", "")
            lines.append(f"- {key}: {enabled}, config={config}")
    else:
        lines.append("- none")

    lines.extend(["", "## Recommended Commands"])
    for command in packet["recommended_commands"]:
        lines.append(f"- `{command}`")

    return "\n".join(lines) + "\n"
