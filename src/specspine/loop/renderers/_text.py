from __future__ import annotations

from typing import Any

from ._text_header import render_header_and_summary
from ._text_features import render_core_features
from ._text_sections import (
    render_context_commands,
    render_lifecycle_steps,
    render_subagents,
    render_validation_commands,
    render_safety_notes,
    render_upstreams,
    render_recommended_commands,
)

__all__ = [
    "render_loop_packet_text",
]


def render_loop_packet_text(packet: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.extend(render_header_and_summary(packet))
    lines.extend(render_core_features(packet))
    lines.extend(render_context_commands(packet))
    lines.extend(render_lifecycle_steps(packet))
    lines.extend(render_subagents(packet))
    lines.extend(render_validation_commands(packet))
    lines.extend(render_safety_notes(packet))
    lines.extend(render_upstreams(packet))
    lines.extend(render_recommended_commands(packet))
    return "\n".join(lines) + "\n"
