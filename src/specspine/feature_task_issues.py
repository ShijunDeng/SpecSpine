from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    FeatureMetadata,
    FeatureTask,
    FeatureTaskIssueDraft,
    FeatureTaskIssuesReport,
    FeatureTraceChecklistItem,
    _relative_feature_paths,
    _render_metadata_lines,
    read_feature_metadata,
    validate_feature_slug,
)
from .feature_trace import build_feature_trace_report
from .feature_tasks_build import build_feature_tasks_report

__all__ = [
    "FeatureTaskIssueDraft",
    "FeatureTaskIssuesReport",
    "build_feature_task_issues_report",
]


def _recommended_task_issue_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature tasks {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        "specspine validate . --fusion --features",
    )


def _truncate_issue_title_text(text: str, *, limit: int = 80) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _feature_task_issue_title(slug: str, task: FeatureTask) -> str:
    return f"[{slug}] {task.id}: {_truncate_issue_title_text(task.text)}"


def _render_task_issue_acceptance_criteria(
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
) -> list[str]:
    if not acceptance_criteria:
        return ["- [ ] Add acceptance criteria checklist items before opening this issue."]

    lines: list[str] = []
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


def build_feature_task_issues_report(root: Path, slug: str) -> FeatureTaskIssuesReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    tasks_report = build_feature_tasks_report(resolved_root, slug)
    try:
        trace_report = build_feature_trace_report(resolved_root, slug)
        acceptance_criteria = trace_report.acceptance_criteria
    except FeatureBundleNotFoundError:
        acceptance_criteria = ()

    metadata = read_feature_metadata(resolved_root, slug)
    recommended_commands = _recommended_task_issue_commands(slug)
    issues = tuple(
        FeatureTaskIssueDraft(
            title=_feature_task_issue_title(slug, task),
            body=_render_task_issue_body(
                feature_id=slug,
                status=tasks_report.status,
                task=task,
                acceptance_criteria=acceptance_criteria,
                recommended_commands=recommended_commands,
                metadata=metadata,
            ),
            feature_id=slug,
            task_id=task.id,
            task_text=task.text,
            task_done=task.done,
            source_file=task.source_file,
            line=task.line,
        )
        for task in tasks_report.tasks
    )

    return FeatureTaskIssuesReport(
        feature_id=slug,
        status=tasks_report.status,
        source_file=tasks_report.source_file,
        source_missing=tasks_report.source_missing,
        missing_files=tasks_report.missing_files,
        issues=issues,
        task_summary=tasks_report.summary,
        recommended_commands=recommended_commands,
    )
