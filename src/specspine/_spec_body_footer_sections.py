from __future__ import annotations

from ._spec_section_content import (
    _generate_constraint_lines,
    _generate_traceability_lines,
)

__all__ = [
    "_render_footer_sections",
]


def _render_footer_sections(resolved_slug: str, criteria: list[dict], parsed: dict) -> str:
    constraint_lines = _generate_constraint_lines(parsed)
    traceability_lines = _generate_traceability_lines(resolved_slug, criteria)
    return (
        "## Constraints\n\n"
        f"{constraint_lines}\n\n"
        "## Traceability Notes\n\n"
        f"{traceability_lines}\n"
    )
