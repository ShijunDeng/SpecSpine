from __future__ import annotations

from ..feature_bundle import FeatureTestsReport
from ..feature_trace import _render_trace_checklist_item

__all__ = [
    "render_test_plan_lines",
    "render_quality_checks_lines",
]


def render_test_plan_lines(report: FeatureTestsReport) -> list[str]:
    lines: list[str] = ["", "Existing Test Plan:"]
    if report.test_plan:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.test_plan
        )
    else:
        lines.append("- None found.")
    return lines


def render_quality_checks_lines(report: FeatureTestsReport) -> list[str]:
    lines: list[str] = ["", "Quality Checks:"]
    if report.quality_checks:
        lines.extend(
            _render_trace_checklist_item(item)
            for item in report.quality_checks
        )
    else:
        lines.append("- None found.")
    return lines
