from __future__ import annotations

from ..feature_bundle_models import FEATURE_PRIORITIES


def normalize_feature_priority(priority: str | None) -> str:
    if priority is None:
        return "unknown"

    normalized = priority.strip().lower()
    if normalized in FEATURE_PRIORITIES:
        return normalized

    return "unknown"


def normalize_feature_owner(owner: str | None) -> str:
    if owner is None:
        return "unassigned"

    normalized = owner.strip()
    if not normalized:
        return "unassigned"
    if normalized.lower() == "unassigned":
        return "unassigned"

    return normalized


def normalize_feature_assignment(value: str | None) -> str:
    if value is None:
        return "unassigned"

    normalized = value.strip()
    if not normalized:
        return "unassigned"
    if normalized.lower() == "unassigned":
        return "unassigned"

    return normalized


def normalize_feature_effort(effort: str | None) -> str:
    if effort is None:
        return "unknown"

    normalized = effort.strip()
    if not normalized:
        return "unknown"
    if normalized.lower() == "unknown":
        return "unknown"

    return normalized


__all__ = [
    "normalize_feature_priority",
    "normalize_feature_owner",
    "normalize_feature_assignment",
    "normalize_feature_effort",
]
