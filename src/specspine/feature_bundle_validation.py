from __future__ import annotations

from .feature_bundle_models import (
    FEATURE_PRIORITIES,
    FEATURE_SLUG_RE,
    FEATURE_STATUSES,
    InvalidFeatureSlug,
    InvalidFeatureStatus,
)

__all__ = [
    "validate_feature_slug",
    "validate_feature_status",
    "normalize_feature_priority",
    "normalize_feature_owner",
    "normalize_feature_assignment",
    "normalize_feature_effort",
    "feature_title",
]


def validate_feature_slug(slug: str) -> str:
    if FEATURE_SLUG_RE.fullmatch(slug):
        return slug

    raise InvalidFeatureSlug(
        f"Invalid feature slug '{slug}'. Use lowercase letters, numbers, and "
        "hyphens only; start and end with a letter or number."
    )


def validate_feature_status(status: str) -> str:
    if status in FEATURE_STATUSES:
        return status

    allowed = ", ".join(FEATURE_STATUSES)
    raise InvalidFeatureStatus(
        f"Invalid feature status '{status}'. Use one of: {allowed}."
    )


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


def feature_title(slug: str, title: str | None = None) -> str:
    if title and title.strip():
        return title.strip()
    return slug.replace("-", " ").title()
