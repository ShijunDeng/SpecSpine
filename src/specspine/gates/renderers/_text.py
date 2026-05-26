from __future__ import annotations

from ..models import QualityGateReport
from ._text_checks import (
    render_commands_lines,
    render_definition_lines,
    render_required_checks_lines,
)
from ._text_summary import render_text_header_lines

__all__ = [
    "render_quality_gate_text",
]


def render_quality_gate_text(report: QualityGateReport) -> str:
    lines = render_text_header_lines(report)
    lines.extend(render_required_checks_lines(report))
    lines.extend(render_definition_lines(report))
    lines.extend(render_commands_lines(report))
    return "\n".join(lines) + "\n"
