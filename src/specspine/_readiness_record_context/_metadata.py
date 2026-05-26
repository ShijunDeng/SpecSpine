from __future__ import annotations

from typing import Any

from ..features import (
    InvalidFeatureSlug,
    read_feature_metadata,
)

__all__ = [
    "extract_slug",
    "extract_status",
    "fetch_feature_metadata",
]


def extract_slug(feature: dict[str, object]) -> str:
    return str(feature["slug"])


def extract_status(feature: dict[str, object]) -> str:
    return str(feature.get("status") or "unknown")


def fetch_feature_metadata(resolved_root, slug: str) -> Any | None:
    try:
        return read_feature_metadata(resolved_root, slug)
    except InvalidFeatureSlug:
        return None
