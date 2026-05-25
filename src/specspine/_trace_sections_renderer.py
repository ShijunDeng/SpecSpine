from __future__ import annotations

from .feature_bundle import FeatureTraceReport
from ._checklist_renderer import _render_trace_checklist_item


def render_trace_gaps(report: FeatureTraceReport) -> list[str]:
    lines = ["", "Gaps:"]
    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")
    return lines


def render_trace_checklist_section(label: str, items: list) -> list[str]:
    lines = ["", f"{label}:"]
    if items:
        lines.extend(_render_trace_checklist_item(item) for item in items)
    else:
        lines.append("- None found.")
    return lines


def render_trace_test_plan(report: FeatureTraceReport) -> list[str]:
    lines = ["", "Test Plan:"]
    if report.test_plan:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.test_plan
        )
    else:
        lines.append("- None found.")
    return lines


__all__ = [
    "render_trace_checklist_section",
    "render_trace_gaps",
    "render_trace_test_plan",
]
