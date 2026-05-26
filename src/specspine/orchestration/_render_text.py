from __future__ import annotations

from ._render_text_conflicts import _render_text_conflicts
from ._render_text_footer import _render_text_footer
from ._render_text_header import _render_text_header
from ._render_text_plan import _render_text_plan

__all__ = [
    "render_orchestration_text",
]


def render_orchestration_text(report) -> str:
    lines: list[str] = []
    _render_text_header(report, lines)
    _render_text_conflicts(report, lines)
    _render_text_plan(report, lines)
    _render_text_footer(report, lines)
    return "\n".join(lines) + "\n"
