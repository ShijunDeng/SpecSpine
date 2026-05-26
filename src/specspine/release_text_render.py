from __future__ import annotations

from .release_models import ReleaseNotesReport
from ._release_summary_render import _render_summary_section
from ._release_features_render import _render_features_section
from ._release_breaking_render import _render_breaking_section, _render_safety_section

__all__ = [
    "render_release_notes_text",
]


def render_release_notes_text(report: ReleaseNotesReport) -> str:
    lines = []
    lines.extend(_render_summary_section(report))
    lines.extend(_render_features_section(report))
    lines.extend(_render_breaking_section(report))
    lines.extend(_render_safety_section(report))
    return "\n".join(lines)
