from __future__ import annotations

from .status_workspace import (
    FEATURE_SUMMARY_READY_VALUES,
    FEATURE_SUMMARY_STATUS_FILTERS,
    InvalidFeatureSummaryOption,
)

__all__ = [
    "parse_feature_summary_status_filters",
    "parse_feature_summary_ready_filter",
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
