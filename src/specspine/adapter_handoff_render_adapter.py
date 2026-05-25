from __future__ import annotations

from ._adapter_handoff_sections import (
    render_header_lines,
    render_adapter_focus_lines,
    render_upstream_artifacts_lines,
    render_local_commands_lines,
    render_upstream_steps_lines,
    render_safety_lines,
    render_notes_lines,
)

__all__ = [
    "render_adapter_feature_handoff_adapter_text",
]


def render_adapter_feature_handoff_adapter_text(
    report,
    adapter_key: str,
) -> str:
    lines = []
    lines.extend(render_header_lines(report, adapter_key))
    lines.extend(render_adapter_focus_lines(report, adapter_key))
    lines.extend(render_upstream_artifacts_lines(report, adapter_key))
    lines.extend(render_local_commands_lines(report, adapter_key))
    lines.extend(render_upstream_steps_lines(report, adapter_key))
    lines.extend(render_safety_lines(report, adapter_key))
    lines.extend(render_notes_lines(report, adapter_key))
    return "\n".join(lines).rstrip() + "\n"
