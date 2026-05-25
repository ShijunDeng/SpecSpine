from __future__ import annotations

from ...features import InvalidFeatureSlug, validate_feature_slug

__all__ = [
    "_feature_slug_from_path",
]


def _feature_slug_from_path(path: str) -> str | None:
    for prefix in ("specs/features/", "execution/features/", "quality/features/"):
        if path.startswith(prefix) and path.endswith(".md"):
            slug = path.removeprefix(prefix).removesuffix(".md")
            if "/" not in slug:
                try:
                    return validate_feature_slug(slug)
                except InvalidFeatureSlug:
                    return None
    return None
