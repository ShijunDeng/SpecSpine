from __future__ import annotations

from ._text_modules import _render_modules_section
from ._text_sections import (
    _render_entities_section,
    _render_error_paths_section,
    _render_safety_notes_section,
)

__all__ = [
    "render_blueprint_text",
]


def render_blueprint_text(report) -> str:
    lines = [
        f"Implementation Blueprint: {report.feature_id}",
        "",
        f"Coverage: {report.coverage_summary['modules_total']} modules, "
        f"{report.coverage_summary['functions_total']} functions, "
        f"{report.coverage_summary['data_entities_total']} entities, "
        f"{report.coverage_summary['error_paths_total']} error paths, "
        f"{report.coverage_summary['unique_ac_covered']} ACs covered",
        "",
    ]

    lines.extend(_render_modules_section(report.modules))
    lines.extend(_render_entities_section(report.data_entities))
    lines.extend(_render_error_paths_section(report.error_paths))
    lines.extend(_render_safety_notes_section(report.safety_notes))

    return "\n".join(lines) + "\n"
