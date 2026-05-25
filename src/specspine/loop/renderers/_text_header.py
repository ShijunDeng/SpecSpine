from __future__ import annotations

from typing import Any

__all__ = [
    "render_header_and_summary",
]


def render_header_and_summary(packet: dict[str, Any]) -> list[str]:
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
    return lines
