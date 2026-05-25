from __future__ import annotations

import shlex

from .adapter_models import (
    ADAPTER_SPECS,
    AdapterHandoffStep,
)


def _render_step_line(step: AdapterHandoffStep) -> str:
    if step.argv:
        command = " ".join(shlex.quote(part) for part in step.argv)
        detail = f"`{command}`"
    else:
        detail = step.instruction
    return (
        f"- {step.id} ({step.kind}): {step.description} "
        f"executed=no safe_to_auto_run=no creates_remote=no "
        f"requires_network=no requires_token=no"
        + (f" - {detail}" if detail else "")
    )


def render_adapter_feature_handoff_text(
    report,
) -> str:
    summary = report.summary
    adapters_summary = summary["adapters"]
    steps_summary = summary["steps"]
    lines = [
        f"# Adapter Feature Handoff: {report.feature_id}",
        "",
        "## Feature",
        "",
        f"- Status: {report.status}",
        f"- Ready: {'yes' if report.ready else 'no'}",
        f"- Source files: {len(report.source_files)}",
        f"- Missing files: {len(report.missing_files)}",
        f"- Gaps: {summary['gaps']['total']}",
        f"- Blocking checks: {summary['blocking_checks']['total']}",
        (
            "- Summary: "
            f"adapters={adapters_summary['total']} "
            f"enabled={adapters_summary['enabled']} "
            f"config_exists={adapters_summary['config_exists']} "
            f"steps={steps_summary['total']}"
        ),
        "",
        "## Sources",
        "",
    ]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(["", "## Gaps", ""])
    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Blocking Checks", ""])
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Adapters", ""])
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

    lines.extend(["## Recommended Local Commands", ""])
    lines.extend(f"- `{command}`" for command in report.recommended_commands)

    return "\n".join(lines).rstrip() + "\n"


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


__all__ = [
    "_render_step_line",
    "render_adapter_feature_handoff_text",
    "render_adapter_feature_handoff_adapter_text",
]
