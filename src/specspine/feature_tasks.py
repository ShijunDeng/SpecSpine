from __future__ import annotations

import json
from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    FeatureMetadata,
    FeatureTask,
    FeatureTaskIssueDraft,
    FeatureTaskIssuesReport,
    FeatureTasksReport,
    FeatureTraceChecklistItem,
    _relative_feature_paths,
    _render_metadata_lines,
    feature_bundle_paths,
    get_feature_status,
    parse_feature_tasks,
    read_feature_metadata,
    validate_feature_slug,
)
from .feature_trace import build_feature_trace_report

__all__ = [
    "FeatureTasksReport",
    "FeatureTaskIssueDraft",
    "FeatureTaskIssuesReport",
    "build_feature_tasks_report",
    "build_feature_task_issues_report",
    "render_feature_task_issues_text",
    "render_feature_task_issues_json",
    "render_feature_tasks_json",
    "render_feature_tasks_text",
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


def build_feature_tasks_report(root: Path, slug: str) -> FeatureTasksReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents: dict[str, str] = {}
    missing_files: list[str] = []
    missing_paths: list[Path] = []

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
            continue

        missing_files.append(relative_path)
        missing_paths.append(path)

    if not contents:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(missing_paths),
        )

    source_file = relative_paths["execution"]
    execution_content = contents.get("execution")
    tasks: tuple[FeatureTask, ...] = ()
    if execution_content is not None:
        tasks = parse_feature_tasks(execution_content, source_file=source_file)

    status_report = get_feature_status(resolved_root, slug)

    return FeatureTasksReport(
        feature_id=slug,
        status=status_report.status or "unknown",
        source_file=source_file,
        source_missing=execution_content is None,
        tasks=tasks,
        missing_files=tuple(missing_files),
    )


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


def render_feature_task_issues_json(report: FeatureTaskIssuesReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_task_issues_text(report: FeatureTaskIssuesReport) -> str:
    summary = report.summary
    lines = [
        f"Feature task issue drafts: {report.feature_id}",
        f"Status: {report.status}",
        f"Source: {report.source_file}",
        (
            "Summary: "
            f"tasks={summary['total']} "
            f"done={summary['done']} "
            f"open={summary['open']} "
            f"issues={summary['issue_total']}"
        ),
        "",
        "Issues:",
    ]

    if report.issues:
        for index, issue in enumerate(report.issues, start=1):
            if index > 1:
                lines.append("")
            lines.extend(
                [
                    f"### Issue {index}: {issue.task_id}",
                    "",
                    f"Title: {issue.title}",
                    "",
                    issue.body.rstrip(),
                ]
            )
    elif report.source_missing:
        lines.append(
            "No issue drafts generated because source file is missing: "
            f"{report.source_file}"
        )
    else:
        lines.append(f"No checklist tasks found in {report.source_file}.")

    if report.missing_files:
        lines.extend(["", "Missing feature files:"])
        lines.extend(f"- {relative_path}" for relative_path in report.missing_files)

    lines.extend(["", "Key Commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"


def render_feature_tasks_json(report: FeatureTasksReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_tasks_text(report: FeatureTasksReport) -> str:
    summary = report.summary
    lines = [
        f"Feature tasks: {report.feature_id}",
        f"Status: {report.status}",
        f"Source: {report.source_file}",
        (
            "Summary: "
            f"total={summary['total']} "
            f"done={summary['done']} "
            f"open={summary['open']}"
        ),
        "",
        "Tasks:",
    ]

    if report.tasks:
        for task in report.tasks:
            marker = "x" if task.done else " "
            lines.append(
                f"- [{marker}] {task.id} {task.source_file}:{task.line} {task.text}"
            )
    elif report.source_missing:
        lines.append(f"No tasks found because source file is missing: {report.source_file}")
    else:
        lines.append(f"No checklist tasks found in {report.source_file}.")

    if report.missing_files:
        lines.extend(["", "Missing feature files:"])
        lines.extend(f"- {relative_path}" for relative_path in report.missing_files)

    return "\n".join(lines) + "\n"
