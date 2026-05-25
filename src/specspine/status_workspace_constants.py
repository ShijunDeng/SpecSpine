from __future__ import annotations

from typing import Any

from .features import FEATURE_STATUSES, FeatureMetadata

FEATURE_SUMMARY_STATUS_FILTERS = (*FEATURE_STATUSES, "invalid", "unknown")
FEATURE_SUMMARY_PRIORITY_FILTERS = ("high", "medium", "low", "unknown")
FEATURE_SUMMARY_READY_VALUES = {
    "yes": True,
    "true": True,
    "ready": True,
    "no": False,
    "false": False,
    "not-ready": False,
}
FEATURE_SUMMARY_SORT_KEYS = (
    "slug",
    "status",
    "ready",
    "gaps",
    "blocking",
    "tasks-open",
    "priority",
    "milestone",
    "target-release",
    "project",
    "effort",
)
_FEATURE_SUMMARY_STATUS_ORDER = {
    status: index
    for index, status in enumerate(FEATURE_STATUSES)
}
_FEATURE_SUMMARY_STATUS_ORDER["invalid"] = len(_FEATURE_SUMMARY_STATUS_ORDER)
_FEATURE_SUMMARY_STATUS_ORDER["unknown"] = len(_FEATURE_SUMMARY_STATUS_ORDER)
_FEATURE_SUMMARY_PRIORITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "unknown": 3,
}
_FEATURE_SUMMARY_EFFORT_ORDER = {
    "xs": 0,
    "s": 1,
    "m": 2,
    "l": 3,
    "xl": 4,
    "xxl": 5,
    "unknown": 6,
}
_FEATURE_SUMMARY_DEFAULT_VALUES = {
    "milestone": "unassigned",
    "target-release": "unassigned",
    "project": "unassigned",
    "effort": "unknown",
}


class InvalidFeatureSummaryOption(ValueError):
    """Raised when a feature summary filter or sort option is unsupported."""


__all__ = [
    "InvalidFeatureSummaryOption",
    "FEATURE_SUMMARY_STATUS_FILTERS",
    "FEATURE_SUMMARY_PRIORITY_FILTERS",
    "FEATURE_SUMMARY_READY_VALUES",
    "FEATURE_SUMMARY_SORT_KEYS",
    "_FEATURE_SUMMARY_STATUS_ORDER",
    "_FEATURE_SUMMARY_PRIORITY_ORDER",
    "_FEATURE_SUMMARY_EFFORT_ORDER",
    "_FEATURE_SUMMARY_DEFAULT_VALUES",
]
