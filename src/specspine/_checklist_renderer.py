from __future__ import annotations

from .feature_bundle import (
    FeatureTraceChecklistItem,
    FeatureTask,
)

__all__ = [
    "_render_trace_checklist_item",
]


def _render_trace_checklist_item(
    item: FeatureTraceChecklistItem | FeatureTask,
) -> str:
    marker = "x" if item.done else " "
    return f"- [{marker}] {item.id} {item.source_file}:{item.line} {item.text}"
