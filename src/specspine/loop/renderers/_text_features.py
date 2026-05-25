from __future__ import annotations

from typing import Any

__all__ = [
    "render_core_features",
]


def render_core_features(packet: dict[str, Any]) -> list[str]:
    lines = ["", "## Core Features"]
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
    return lines
