from __future__ import annotations

from typing import Any

from ._render_plan_header import _render_plan_header_lines
from ._render_plan_steps import _render_blocked_steps_lines, _render_plan_steps_lines
from ._render_plan_footer import _render_footer_lines

__all__ = [
    "render_plan_text",
]


def render_plan_text(result: dict[str, Any]) -> str:
    lines = _render_plan_header_lines(result)
    lines.extend(_render_plan_steps_lines(result))
    lines.extend(_render_blocked_steps_lines(result))
    lines.extend(_render_footer_lines(result))
    return "\n".join(lines) + "\n"
