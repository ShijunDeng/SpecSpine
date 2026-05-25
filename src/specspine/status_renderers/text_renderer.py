from __future__ import annotations

from typing import Any

from .text_markers import _complete_marker, _marker  # noqa: F401
from .text_header import _render_text_header
from .text_adapters_validation import _render_text_adapters, _render_text_validation
from .text_summaries import (
    _render_text_feature_summaries,
    _render_text_readiness_summary,
    _render_text_recommendations,
)

__all__ = [
    "_complete_marker",
    "_marker",
    "_render_text_header",
    "_render_text_adapters",
    "_render_text_validation",
    "_render_text_feature_summaries",
    "_render_text_readiness_summary",
    "_render_text_recommendations",
    "render_status_text",
]


def render_status_text(status: dict[str, Any]) -> str:
    lines: list[str] = []
    _render_text_header(status, lines)
    _render_text_adapters(status, lines)
    _render_text_validation(status, lines)
    _render_text_feature_summaries(status, lines)
    _render_text_readiness_summary(status, lines)
    _render_text_recommendations(status, lines)
    return "\n".join(lines) + "\n"
