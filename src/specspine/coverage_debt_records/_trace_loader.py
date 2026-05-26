from __future__ import annotations

from ..features import build_feature_trace_report

__all__ = [
    "_build_trace_report",
]


def _build_trace_report(root, slug: str) -> dict:
    return build_feature_trace_report(root, slug)
