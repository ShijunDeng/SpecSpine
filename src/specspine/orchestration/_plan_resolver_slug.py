from __future__ import annotations

from pathlib import Path

from ..features import validate_feature_slug

__all__ = [
    "_resolve_slugs",
]


def _resolve_slugs(
    resolved_root: Path,
    all_slugs: list[str],
    feature_filter: str | None,
) -> str | None:
    if feature_filter is not None:
        try:
            feature_filter = validate_feature_slug(feature_filter)
        except ValueError:
            raise
    if feature_filter is not None:
        slugs = [feature_filter] if feature_filter in all_slugs else []
    else:
        slugs = list(all_slugs)
    return slugs
