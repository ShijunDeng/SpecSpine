from __future__ import annotations

from .feature_bundle import FeatureTraceReport
from ._trace_header_renderer import render_trace_header
from ._trace_sections_renderer import (
    render_trace_gaps,
    render_trace_checklist_section,
    render_trace_test_plan,
)

__all__ = [
    "render_feature_trace_text",
]


def render_feature_trace_text(report: FeatureTraceReport) -> str:
    lines = render_trace_header(report)
    lines.extend(render_trace_gaps(report))
    lines.extend(render_trace_checklist_section("Acceptance Criteria", report.acceptance_criteria))
    lines.extend(render_trace_checklist_section("Tasks", report.tasks))
    lines.extend(render_trace_checklist_section("Quality Checks", report.quality_checks))
    lines.extend(render_trace_test_plan(report))
    return "\n".join(lines) + "\n"
