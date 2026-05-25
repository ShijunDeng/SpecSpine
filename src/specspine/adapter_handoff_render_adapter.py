from __future__ import annotations

from .adapter_handoff_render_step import _render_step_line

__all__ = [
    "render_adapter_feature_handoff_adapter_text",
]


def render_adapter_feature_handoff_adapter_text(
    report,
    adapter_key: str,
) -> str:
    adapter = report.adapters[adapter_key]
    lines = [
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
        "## Upstream Artifacts",
        "",
    ]
    if adapter.upstream_artifacts:
        lines.extend(f"- {artifact}" for artifact in adapter.upstream_artifacts)
    else:
        lines.append("- None.")

    lines.extend(["", "## Local Commands", ""])
    if adapter.local_commands:
        lines.extend(f"- `{command}`" for command in adapter.local_commands)
    else:
        lines.append("- None.")

    lines.extend(["", "## Recommended Upstream Steps", ""])
    if adapter.recommended_upstream_steps:
        lines.extend(_render_step_line(step) for step in adapter.recommended_upstream_steps)
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
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
            "## Notes",
            "",
        ]
    )
    lines.extend(f"- {note}" for note in adapter.notes)
    return "\n".join(lines).rstrip() + "\n"
