from __future__ import annotations

from .status_workspace import (
    FEATURE_SUMMARY_READY_VALUES,
    FEATURE_SUMMARY_SORT_KEYS,
    FEATURE_SUMMARY_STATUS_FILTERS,
    InvalidFeatureSummaryOption,
    _FEATURE_SUMMARY_DEFAULT_VALUES,
)

from .status_features_models import FEATURE_SUMMARY_PRIORITY_FILTERS_LOCAL

__all__ = [
    "parse_feature_summary_status_filters",
    "parse_feature_summary_ready_filter",
    "parse_feature_summary_priority_filters",
    "parse_feature_summary_owner_filters",
    "parse_feature_summary_metadata_filters",
    "parse_feature_summary_sort_key",
]


def parse_feature_summary_status_filters(values: list[str] | None) -> tuple[str, ...]:
    statuses: list[str] = []
    for value in values or []:
        normalized = value.strip().lower()
        if normalized not in FEATURE_SUMMARY_STATUS_FILTERS:
            allowed = ", ".join(FEATURE_SUMMARY_STATUS_FILTERS)
            raise InvalidFeatureSummaryOption(
                f"Invalid feature summary status '{value}'. Use one of: {allowed}."
            )
        if normalized not in statuses:
            statuses.append(normalized)

    return tuple(statuses)


def parse_feature_summary_ready_filter(value: str | None) -> bool | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if normalized not in FEATURE_SUMMARY_READY_VALUES:
        allowed = ", ".join(FEATURE_SUMMARY_READY_VALUES)
        raise InvalidFeatureSummaryOption(
            f"Invalid feature summary readiness '{value}'. Use one of: {allowed}."
        )

    return FEATURE_SUMMARY_READY_VALUES[normalized]


def parse_feature_summary_priority_filters(values: list[str] | None) -> tuple[str, ...]:
    priorities: list[str] = []
    for value in values or []:
        normalized = value.strip().lower()
        if normalized not in FEATURE_SUMMARY_PRIORITY_FILTERS_LOCAL:
            allowed = ", ".join(FEATURE_SUMMARY_PRIORITY_FILTERS_LOCAL)
            raise InvalidFeatureSummaryOption(
                f"Invalid feature summary priority '{value}'. Use one of: {allowed}."
            )
        if normalized not in priorities:
            priorities.append(normalized)

    return tuple(priorities)


def parse_feature_summary_owner_filters(values: list[str] | None) -> tuple[str, ...]:
    owners: list[str] = []
    for value in values or []:
        normalized = value.strip().lower() or "unassigned"
        if normalized not in owners:
            owners.append(normalized)

    return tuple(owners)


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
