from __future__ import annotations

__all__ = [
    "_resolve_and_validate_slug",
]


def _resolve_and_validate_slug(slug: str | None) -> str | None:
    from .features import validate_feature_slug

    if slug is not None:
        return validate_feature_slug(slug)
    return slug
