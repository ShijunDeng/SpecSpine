from __future__ import annotations

from ..feature_bundle import FeatureTestsReport
from ._header import render_header_lines
from ._sections import render_section_lines

__all__ = [
    "render_feature_tests_text",
]


def render_feature_tests_text(report: FeatureTestsReport) -> str:
    lines = render_header_lines(report)
    lines.extend(render_section_lines(report))
    return "\n".join(lines) + "\n"
