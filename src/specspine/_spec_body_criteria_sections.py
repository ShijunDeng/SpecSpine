from __future__ import annotations

from ._spec_section_content import (
    _generate_ac_lines,
    _generate_edge_case_lines,
)

__all__ = [
    "_render_criteria_sections",
]


def _render_criteria_sections(parsed: dict, criteria: list[dict]) -> str:
    ac_lines = _generate_ac_lines(criteria)
    edge_case_lines = _generate_edge_case_lines(parsed)
    return (
        "## Acceptance Criteria\n\n"
        f"{ac_lines}\n\n"
        "## Edge Cases\n\n"
        f"{edge_case_lines}\n"
    )
