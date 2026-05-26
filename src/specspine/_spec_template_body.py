from __future__ import annotations

from ._spec_body_header_sections import _render_header_sections
from ._spec_body_criteria_sections import _render_criteria_sections
from ._spec_body_footer_sections import _render_footer_sections

__all__ = [
    "build_body_sections",
]


def build_body_sections(
    parsed: dict,
    criteria: list[dict],
    intent: str,
    resolved_slug: str,
) -> str:
    header = _render_header_sections(parsed, intent)
    criteria_sections = _render_criteria_sections(parsed, criteria)
    footer = _render_footer_sections(resolved_slug, criteria, parsed)
    return f"\n{header}\n{criteria_sections}\n{footer}"
