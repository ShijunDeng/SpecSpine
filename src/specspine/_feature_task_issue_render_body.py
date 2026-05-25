from __future__ import annotations

from .feature_bundle import (
    FeatureMetadata,
    FeatureTask,
    FeatureTraceChecklistItem,
    _render_metadata_lines,
)

__all__ = [
    "_render_task_issue_acceptance_criteria",
    "_render_task_issue_commands",
    "_render_task_issue_body",
]


def _render_task_issue_acceptance_criteria(
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
) -> list[str]:
    if not acceptance_criteria:
        return ["- [ ] Add acceptance criteria checklist items before opening this issue."]

    lines = []
    for item in acceptance_criteria:
        marker = "x" if item.done else " "
        lines.append(
            f"- [{marker}] {item.id} {item.source_file}:{item.line} {item.text}"
        )
    return lines


def _render_task_issue_commands(commands: tuple[str, ...]) -> list[str]:
    return [f"- `{command}`" for command in commands]


def _render_task_issue_body(
    *,
    feature_id: str,
    status: str,
    task: FeatureTask,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    recommended_commands: tuple[str, ...],
    metadata: FeatureMetadata,
) -> str:
    marker = "x" if task.done else " "
    lines = [
        "## Feature",
        "",
        f"- Feature ID: `{feature_id}`",
        f"- Status: {status}",
        "",
        "## Metadata",
        "",
        *_render_metadata_lines(metadata),
        "",
        "## Task",
        "",
        f"- [{marker}] {task.id}: {task.text}",
        "",
        "## Status / Done",
        "",
        f"- Done: {'yes' if task.done else 'no'}",
        "",
        "## Source",
        "",
        f"- {task.source_file}:{task.line}",
        "",
        "## Acceptance Criteria",
        "",
    ]
    lines.extend(_render_task_issue_acceptance_criteria(acceptance_criteria))
    lines.extend(["", "## Key Commands", ""])
    lines.extend(_render_task_issue_commands(recommended_commands))
    return "\n".join(lines).strip() + "\n"
