from __future__ import annotations

from ..feature_bundle import FeatureTestsReport
from ._section_gaps_commands import (
    render_blocking_checks_lines,
    render_gaps_lines,
    render_key_commands_lines,
)
from ._section_plan_quality import (
    render_quality_checks_lines,
    render_test_plan_lines,
)
from ._section_tests import render_test_cases_lines, render_test_coverage_lines

__all__ = [
    "render_section_lines",
]


def render_section_lines(report: FeatureTestsReport) -> list[str]:
    lines: list[str] = []
    lines.extend(render_test_cases_lines(report))
    lines.extend(render_test_coverage_lines(report))
    lines.extend(render_test_plan_lines(report))
    lines.extend(render_quality_checks_lines(report))
    lines.extend(render_gaps_lines(report))
    lines.extend(render_blocking_checks_lines(report))
    lines.extend(render_key_commands_lines(report))
    return lines
