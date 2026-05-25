from __future__ import annotations

__all__ = [
    "InvalidFeatureSlug",
    "InvalidFeatureStatus",
]


class InvalidFeatureSlug(ValueError):
    """Raised when a feature slug cannot be used as a feature id."""


class InvalidFeatureStatus(ValueError):
    """Raised when a feature lifecycle status is not supported."""
