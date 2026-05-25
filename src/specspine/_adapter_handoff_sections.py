from __future__ import annotations

from .adapter_handoff_render_step import _render_step_line

__all__ = [
    "render_header_lines",
    "render_adapter_focus_lines",
    "render_upstream_artifacts_lines",
    "render_local_commands_lines",
    "render_upstream_steps_lines",
    "render_safety_lines",
    "render_notes_lines",
]


def render_header_lines(report, adapter_key: str) -> list[str]:
    adapter = report.adapters[adapter_key]
    return [
        f"# {adapter.display_name} Adapter Handoff: {report.feature_id}",
        "",
        "## Feature",
        "",
        f"- Status: {report.status}",
        f"- Ready: {'yes' if report.ready else 'no'}",
        f"- Missing files: {len(report.missing_files)}",
        f"- Gaps: {len(report.gaps)}",
        f"- Blocking checks: {len(report.blocking_checks)}",
        "",
    ]


def render_adapter_focus_lines(report, adapter_key: str) -> list[str]:
    adapter = report.adapters[adapter_key]
    return [
        "## Adapter Focus",
        "",
        f"- Adapter: {adapter.display_name} ({adapter.key})",
        f"- Enabled: {'yes' if adapter.enabled else 'no'}",
        f"- Config: {adapter.config} (exists: {'yes' if adapter.config_exists else 'no'})",
        f"- Upstream: {adapter.upstream_url}",
        f"- Integration surface: {adapter.integration_surface}",
        f"- Native status: {adapter.native_status}",
        f"- Upstream phase: {adapter.upstream_phase}",
        f"- Agent focus: {adapter.agent_focus}",
        "",
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


def render_safety_lines(report, adapter_key: str) -> list[str]:
    return [
        "## Safety",
        "",
        "- executed=false",
        "- requires_network=false",
        "- requires_token=false",
        "- creates_remote=false",
        "- safe_to_auto_run=false",
        (
            "- Artifact export does not execute upstream tools, subprocesses, "
            "network calls, GitHub operations, or token reads."
        ),
        "",
    ]


def render_notes_lines(report, adapter_key: str) -> list[str]:
    adapter = report.adapters[adapter_key]
    lines = ["## Notes", ""]
    lines.extend(f"- {note}" for note in adapter.notes)
    return lines
