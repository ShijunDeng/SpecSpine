from __future__ import annotations

from ._consistency_text_renderer import (
    render_consistency_text,
)
from ._summary_builder import (
    _summary,
)

__all__ = [
    "_summary",
    "render_consistency_text",
]

_summary = _summary
render_consistency_text = render_consistency_text
