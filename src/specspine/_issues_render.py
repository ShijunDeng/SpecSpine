from __future__ import annotations

import json

from .feature_bundle import FeatureTaskIssuesReport

__all__ = [
    "render_feature_task_issues_json",
    "render_feature_task_issues_text",
]


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
