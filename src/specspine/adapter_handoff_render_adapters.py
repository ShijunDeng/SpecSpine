from __future__ import annotations

from .adapter_models import ADAPTER_SPECS
from .adapter_handoff_render_step import _render_step_line

__all__ = [
    "_render_adapters_section",
]


def _render_adapters_section(report) -> list[str]:
    lines = ["", "## Adapters", ""]
    for key in ADAPTER_SPECS:
        adapter = report.adapters[key]
        lines.extend(
            [
                f"### {adapter.display_name} ({adapter.key})",
                "",
                f"- Enabled: {'yes' if adapter.enabled else 'no'}",
                f"- Config: {adapter.config} (exists: {'yes' if adapter.config_exists else 'no'})",
                f"- Upstream: {adapter.upstream_url}",
                f"- Integration surface: {adapter.integration_surface}",
                f"- Native status: {adapter.native_status}",
                f"- Upstream phase: {adapter.upstream_phase}",
                f"- Agent focus: {adapter.agent_focus}",
                "- Upstream artifacts:",
            ]
        )
        if adapter.upstream_artifacts:
            lines.extend(f"  - {artifact}" for artifact in adapter.upstream_artifacts)
        else:
            lines.append("  - None.")
        lines.append("- Local commands:")
        if adapter.local_commands:
            lines.extend(f"  - `{command}`" for command in adapter.local_commands)
        else:
            lines.append("  - None.")
        lines.append("- Recommended upstream steps:")
        if adapter.recommended_upstream_steps:
            lines.extend(
                f"  {_render_step_line(step)}"
                for step in adapter.recommended_upstream_steps
            )
        else:
            lines.append("  - None.")
        lines.append("- Notes:")
        lines.extend(f"  - {note}" for note in adapter.notes)
        lines.append("")
    return lines
