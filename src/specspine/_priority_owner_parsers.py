from __future__ import annotations

from .status_workspace import InvalidFeatureSummaryOption

from .status_features_models import FEATURE_SUMMARY_PRIORITY_FILTERS_LOCAL

__all__ = [
    "parse_feature_summary_priority_filters",
    "parse_feature_summary_owner_filters",
]


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
