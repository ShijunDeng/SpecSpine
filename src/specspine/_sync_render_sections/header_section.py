from __future__ import annotations

from ..feature_bundle import (
    FeatureSyncPlan,
    _render_metadata_lines,
)

__all__ = [
    "_render_header_lines",
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
