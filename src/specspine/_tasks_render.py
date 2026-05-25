from __future__ import annotations

import json

from .feature_bundle import FeatureTasksReport

__all__ = [
    "render_feature_tasks_json",
    "render_feature_tasks_text",
]


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
