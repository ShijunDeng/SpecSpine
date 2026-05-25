from __future__ import annotations

import json
import shlex

from .feature_bundle import (
    FeatureSyncPlan,
    _render_metadata_lines,
)

__all__ = [
    "render_feature_sync_plan_json",
    "render_feature_sync_plan_text",
]


def render_feature_sync_plan_json(plan: FeatureSyncPlan) -> str:
    return json.dumps(plan.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_sync_plan_text(plan: FeatureSyncPlan) -> str:
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
            f"feature_issues={summary['issue_commands']} "
            f"task_issues={summary['task_issue_commands']} "
            f"pull_requests={summary['pull_request_commands']}"
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

    lines.extend(["", "## Sources", ""])
    if plan.source_files:
        lines.extend(f"- [ok] {relative_path}" for relative_path in plan.source_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Missing Files", ""])
    if plan.missing_files:
        lines.extend(f"- [missing] {relative_path}" for relative_path in plan.missing_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Gaps", ""])
    if plan.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in plan.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Blocking Checks", ""])
    if plan.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in plan.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Commands", ""])
    for command in plan.commands:
        lines.extend(
            [
                f"### {command.id}",
                "",
                f"- Kind: {command.kind}",
                f"- Description: {command.description}",
                f"- Body source: {command.body_source}",
                f"- Creates remote: {'yes' if command.creates_remote else 'no'}",
                f"- Requires token: {'yes' if command.requires_token else 'no'}",
                f"- Requires network: {'yes' if command.requires_network else 'no'}",
                (
                    "- Safe to auto-run: "
                    f"{'yes' if command.safe_to_auto_run else 'no'}"
                ),
                f"- Command: `{shlex.join(command.argv)}`",
                "",
            ]
        )

    lines.extend(["## Recommended Local Commands", ""])
    lines.extend(f"- `{command}`" for command in plan.recommended_commands)

    return "\n".join(lines).rstrip() + "\n"
