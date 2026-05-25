from __future__ import annotations

import json

from .feature_bundle import (
    FeatureHandoffReport,
)

__all__ = [
    "render_feature_handoff_text",
    "render_feature_handoff_json",
]


def render_feature_handoff_json(report: FeatureHandoffReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_handoff_text(report: FeatureHandoffReport) -> str:
    summary = report.summary
    trace = summary["trace"]
    ready = summary["ready"]
    tasks = summary["tasks"]
    lines = [
        f"Feature handoff: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        (
            "Metadata: "
            f"priority={report.metadata.priority} "
            f"owner={report.metadata.owner} "
            f"milestone={report.metadata.milestone} "
            f"target_release={report.metadata.target_release}"
        ),
        (
            "Counts: "
            f"trace={trace['total']}/{trace['done']}/{trace['open']} "
            f"ready={ready['pass']}/{ready['fail']}/{ready['total']} "
            f"tasks={tasks['total']}/{tasks['done']}/{tasks['open']} "
            f"gaps={summary['gaps']['total']} "
            f"blocking={summary['blocking_checks']['total']}"
        ),
        "Sources:",
    ]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(["", "Next actions:"])
    if report.next_actions:
        lines.extend(f"- {action}" for action in report.next_actions)
    else:
        lines.append("- None.")

    open_tasks = tuple(task for task in report.tasks if not task.done)
    lines.extend(["", "Open tasks:"])
    if open_tasks:
        lines.extend(
            f"- {task.id} {task.source_file}:{task.line} {task.text}"
            for task in open_tasks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Blocking checks:"])
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Key commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"
