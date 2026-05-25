from __future__ import annotations

from .features import FEATURE_PRIORITIES

__all__ = [
    "FEATURE_SUMMARY_PRIORITY_FILTERS_LOCAL",
]

FEATURE_SUMMARY_PRIORITY_FILTERS_LOCAL = (*FEATURE_PRIORITIES, "unknown")
