from __future__ import annotations

from .status_workspace import (
    FEATURE_SUMMARY_SORT_KEYS,
    InvalidFeatureSummaryOption,
)

__all__ = [
    "parse_feature_summary_metadata_filters",
    "parse_feature_summary_sort_key",
]


def parse_feature_summary_metadata_filters(
    values: list[str] | None,
    *,
    default: str,
) -> tuple[str, ...]:
    filters: list[str] = []
    for value in values or []:
        normalized = value.strip().lower() or default
        if normalized not in filters:
            filters.append(normalized)

    return tuple(filters)


def parse_feature_summary_sort_key(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if normalized not in FEATURE_SUMMARY_SORT_KEYS:
        allowed = ", ".join(FEATURE_SUMMARY_SORT_KEYS)
        raise InvalidFeatureSummaryOption(
            f"Invalid feature summary sort key '{value}'. Use one of: {allowed}."
        )

    return normalized
