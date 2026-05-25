from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureBundleNotFoundError,
    FeatureMetadata,
    FeatureTask,
    FeatureTaskIssueDraft,
    FeatureTaskIssuesReport,
    read_feature_metadata,
    validate_feature_slug,
)
from .feature_trace import build_feature_trace_report
from .feature_tasks_build import build_feature_tasks_report
from ._feature_task_issue_render import (
    _feature_task_issue_title,
    _render_task_issue_body,
    _recommended_task_issue_commands,
)

__all__ = [
    "FeatureTaskIssueDraft",
    "FeatureTaskIssuesReport",
    "build_feature_task_issues_report",
]


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
