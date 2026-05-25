from __future__ import annotations

from ._handoff_text_render_header import _render_handoff_header
from ._handoff_text_render_sections import _render_handoff_sections
from .feature_bundle import FeatureHandoffReport

__all__ = [
    "render_feature_handoff_text",
]


def render_feature_handoff_text(report: FeatureHandoffReport) -> str:
    lines = _render_handoff_header(report)
    lines.extend(_render_handoff_sections(report))
    return "\n".join(lines) + "\n"
