from __future__ import annotations

import json
import shlex

from .adapter_models import (
    ADAPTER_HANDOFF_SAFETY_FLAGS,
    ADAPTER_SPECS,
    AdapterFeatureHandoffReport,
    AdapterHandoffStep,
)

__all__ = [
    "_adapter_handoff_blocking_checks",
    "_render_step_line",
    "adapter_feature_handoff_focused_payload",
    "render_adapter_feature_handoff_adapter_json",
    "render_adapter_feature_handoff_adapter_text",
    "render_adapter_feature_handoff_json",
    "render_adapter_feature_handoff_text",
]


def render_adapter_feature_handoff_json(report: AdapterFeatureHandoffReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def _adapter_handoff_blocking_checks(
    report: AdapterFeatureHandoffReport,
) -> list[dict[str, object]]:
    return [
        check.as_dict() if hasattr(check, "as_dict") else dict(check)
        for check in report.blocking_checks
    ]


def adapter_feature_handoff_focused_payload(
    report: AdapterFeatureHandoffReport,
    adapter_key: str,
) -> dict[str, object]:
    return {
        "adapter": report.adapters[adapter_key].as_dict(),
        "blocking_checks": _adapter_handoff_blocking_checks(report),
        "feature_id": report.feature_id,
        "gaps": [dict(gap) for gap in report.gaps],
        "missing_files": list(report.missing_files),
        "ready": report.ready,
        "recommended_commands": list(report.recommended_commands),
        "safety_flags": dict(ADAPTER_HANDOFF_SAFETY_FLAGS),
        "source_files": list(report.source_files),
        "status": report.status,
        "summary": report.summary,
    }


def render_adapter_feature_handoff_adapter_json(
    report: AdapterFeatureHandoffReport,
    adapter_key: str,
) -> str:
    return (
        json.dumps(
            adapter_feature_handoff_focused_payload(report, adapter_key),
            indent=2,
            sort_keys=True,
        )
        + "\n"
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
    report: AdapterFeatureHandoffReport,
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
    report: AdapterFeatureHandoffReport,
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
