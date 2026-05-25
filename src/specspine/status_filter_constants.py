from __future__ import annotations

from .features import FEATURE_STATUSES

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


class InvalidFeatureSummaryOption(ValueError):
    """Raised when a feature summary filter or sort option is unsupported."""


__all__ = [
    "InvalidFeatureSummaryOption",
    "FEATURE_SUMMARY_STATUS_FILTERS",
    "FEATURE_SUMMARY_PRIORITY_FILTERS",
    "FEATURE_SUMMARY_READY_VALUES",
]
