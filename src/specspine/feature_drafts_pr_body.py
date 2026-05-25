from __future__ import annotations

from .feature_bundle import (
    FeatureMetadata,
    FeatureReadyCheck,
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
    _render_metadata_lines,
)
from .feature_drafts_pr_renderers import (
    _render_pr_checklist_items,
    _render_pr_test_plan_items,
    _render_pr_ready_checks,
)

__all__ = [
    "_render_pull_request_body",
]


def _render_pull_request_body(
    *,
    feature_id: str,
    status: str,
    ready: bool,
    summary: dict[str, object],
    why: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    tasks: tuple[FeatureTask, ...],
    test_plan: tuple[FeatureTraceTestPlanItem, ...],
    release_readiness: tuple[FeatureTraceChecklistItem, ...],
    readiness_checks: tuple[FeatureReadyCheck, ...],
    source_files: tuple[str, ...],
    missing_files: tuple[str, ...],
    gaps: tuple[dict[str, str], ...],
    recommended_commands: tuple[str, ...],
    metadata: FeatureMetadata,
) -> str:
    trace = summary["trace"]
    ready_summary = summary["ready"]
    task_summary = summary["tasks"]
    lines = [
        "## Summary",
        "",
        f"- Feature ID: `{feature_id}`",
        f"- Status: {status}",
        f"- Ready: {'yes' if ready else 'no'}",
        (
            "- Trace: "
            f"total={trace['total']} "
            f"done={trace['done']} "
            f"open={trace['open']}"
        ),
        (
            "- Tasks: "
            f"total={task_summary['total']} "
            f"done={task_summary['done']} "
            f"open={task_summary['open']}"
        ),
        (
            "- Readiness: "
            f"pass={ready_summary['pass']} "
            f"fail={ready_summary['fail']} "
            f"total={ready_summary['total']}"
        ),
        "",
        "## Metadata",
        "",
        *_render_metadata_lines(metadata),
        "",
        "## Feature",
        "",
        "- This is an offline Pull Request draft generated from local SpecSpine feature artifacts.",
        "- No remote PR is created by this command.",
        "",
        "## Why",
        "",
        why,
        "",
        "## Acceptance Criteria",
        "",
    ]
    lines.extend(
        _render_pr_checklist_items(
            acceptance_criteria,
            empty_text="Add acceptance criteria checklist items before review.",
        )
    )

    lines.extend(["", "## Tasks", ""])
    lines.extend(
        _render_pr_checklist_items(
            tasks,
            empty_text="Add execution task checklist items before review.",
        )
    )

    lines.extend(["", "## Test Plan", ""])
    lines.extend(
        _render_pr_test_plan_items(
            test_plan,
            empty_text="Add a concrete test plan before review.",
        )
    )

    lines.extend(["", "## Release Readiness", ""])
    lines.extend(
        _render_pr_checklist_items(
            release_readiness,
            empty_text="Add release readiness checklist items before review.",
        )
    )

    lines.extend(["", "## Readiness / Blocking Checks", ""])
    lines.extend(_render_pr_ready_checks(readiness_checks))

    lines.extend(["", "## Gaps", ""])
    if gaps:
        lines.extend(
            f"- [ ] {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in gaps
        )
    else:
        lines.append("- [x] None.")

    lines.extend(["", "## Source Files", ""])
    if source_files:
        lines.extend(f"- {relative_path}" for relative_path in source_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Missing Files", ""])
    if missing_files:
        lines.extend(f"- [ ] {relative_path}" for relative_path in missing_files)
    else:
        lines.append("- [x] None.")

    lines.extend(["", "## Key Commands", ""])
    lines.extend(f"- `{command}`" for command in recommended_commands)

    return "\n".join(lines).strip() + "\n"
