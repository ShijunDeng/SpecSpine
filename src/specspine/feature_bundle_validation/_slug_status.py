from __future__ import annotations

from ..feature_bundle_models import (
    FEATURE_SLUG_RE,
    FEATURE_STATUSES,
    InvalidFeatureSlug,
    InvalidFeatureStatus,
)


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


__all__ = [
    "validate_feature_slug",
    "validate_feature_status",
]
