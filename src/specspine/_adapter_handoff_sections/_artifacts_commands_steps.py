from __future__ import annotations

from ..adapter_handoff_render_step import _render_step_line

__all__ = [
    "render_upstream_artifacts_lines",
    "render_local_commands_lines",
    "render_upstream_steps_lines",
]


def render_upstream_artifacts_lines(report, adapter_key: str) -> list[str]:
    adapter = report.adapters[adapter_key]
    lines = ["## Upstream Artifacts", ""]
    if adapter.upstream_artifacts:
        lines.extend(f"- {artifact}" for artifact in adapter.upstream_artifacts)
    else:
        lines.append("- None.")
    lines.append("")
    return lines


def render_local_commands_lines(report, adapter_key: str) -> list[str]:
    adapter = report.adapters[adapter_key]
    lines = ["## Local Commands", ""]
    if adapter.local_commands:
        lines.extend(f"- `{command}`" for command in adapter.local_commands)
    else:
        lines.append("- None.")
    lines.append("")
    return lines


def render_upstream_steps_lines(report, adapter_key: str) -> list[str]:
    adapter = report.adapters[adapter_key]
    lines = ["## Recommended Upstream Steps", ""]
    if adapter.recommended_upstream_steps:
        lines.extend(_render_step_line(step) for step in adapter.recommended_upstream_steps)
    else:
        lines.append("- None.")
    lines.append("")
    return lines
