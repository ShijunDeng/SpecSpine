from __future__ import annotations

import json

from .feature_bundle import (
    FeatureTraceChecklistItem,
    FeatureTask,
    FeatureTraceReport,
    FeatureTraceTestPlanItem,
)

__all__ = [
    "_render_trace_checklist_item",
    "render_feature_trace_text",
    "render_feature_trace_json",
]


def _render_trace_checklist_item(
    item: FeatureTraceChecklistItem | FeatureTask,
) -> str:
    marker = "x" if item.done else " "
    return f"- [{marker}] {item.id} {item.source_file}:{item.line} {item.text}"


def render_feature_trace_text(report: FeatureTraceReport) -> str:
    summary = report.summary
    lines = [
        f"Feature trace: {report.feature_id}",
        f"Status: {report.status}",
        "Sources:",
    ]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(
        [
            (
                "Summary: "
                f"total={summary['total']} "
                f"done={summary['done']} "
                f"open={summary['open']}"
            ),
            (
                "Counts: "
                f"ac={summary['acceptance_criteria']['total']} "
                f"tasks={summary['tasks']['total']} "
                f"quality={summary['quality_checks']['total']} "
                f"test_plan={summary['test_plan']['total']}"
            ),
            "",
            "Gaps:",
        ]
    )

    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Acceptance Criteria:"])
    if report.acceptance_criteria:
        lines.extend(
            _render_trace_checklist_item(item)
            for item in report.acceptance_criteria
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Tasks:"])
    if report.tasks:
        lines.extend(_render_trace_checklist_item(task) for task in report.tasks)
    else:
        lines.append("- None found.")

    lines.extend(["", "Quality Checks:"])
    if report.quality_checks:
        lines.extend(
            _render_trace_checklist_item(item)
            for item in report.quality_checks
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Test Plan:"])
    if report.test_plan:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.test_plan
        )
    else:
        lines.append("- None found.")

    return "\n".join(lines) + "\n"


def render_feature_trace_json(report: FeatureTraceReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
