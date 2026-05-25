from __future__ import annotations

from ._archive_render_header import _build_archive_header_lines
from ._archive_render_sections import _build_archive_body_lines
from .archive_models import FeatureArchiveReport

__all__ = [
    "render_feature_archive_text",
]


def render_feature_archive_text(report: FeatureArchiveReport) -> str:
    lines = _build_archive_header_lines(report)
    lines.extend(_build_archive_body_lines(report))
    return "\n".join(lines).rstrip() + "\n"
