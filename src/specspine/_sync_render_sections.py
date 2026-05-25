from __future__ import annotations

from .feature_bundle import (
    FeatureSyncPlan,
    _render_metadata_lines,
)

__all__ = [
    "_render_header_lines",
    "_render_source_lines",
    "_render_gap_lines",
    "_render_blocking_lines",
]


def _render_header_lines(plan: FeatureSyncPlan) -> list[str]:
    summary = plan.summary
    lines = [
        f"# GitHub Sync Plan: {plan.feature_id}",
        "",
        "## Summary",
        "",
        f"- Status: {plan.status}",
        f"- Ready: {'yes' if plan.ready else 'no'}",
        (
            "- Commands: "
            f"total={summary['commands_total']} "
            f"issue_commands={summary['issue_commands']} "
            f"task_issue_commands={summary['task_issue_commands']} "
            f"pull_request_commands={summary['pull_request_commands']}"
        ),
        f"- Notes: {summary['notes_total']}",
        "",
        "## Metadata",
        "",
        *_render_metadata_lines(plan.metadata),
        "",
        "## Notes",
        "",
    ]
    lines.extend(f"- {note}" for note in plan.notes)
    return lines


def _render_source_lines(plan: FeatureSyncPlan) -> list[str]:
    lines = ["", "## Sources", ""]
    if plan.source_files:
        lines.extend(f"- [ok] {relative_path}" for relative_path in plan.source_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Missing Files", ""])
    if plan.missing_files:
        lines.extend(f"- [missing] {relative_path}" for relative_path in plan.missing_files)
    else:
        lines.append("- None.")
    return lines


def _render_gap_lines(plan: FeatureSyncPlan) -> list[str]:
    lines = ["", "## Gaps", ""]
    if plan.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in plan.gaps
        )
    else:
        lines.append("- None.")
    return lines


def _render_blocking_lines(plan: FeatureSyncPlan) -> list[str]:
    lines = ["", "## Blocking Checks", ""]
    if plan.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in plan.blocking_checks
        )
    else:
        lines.append("- None.")
    return lines
