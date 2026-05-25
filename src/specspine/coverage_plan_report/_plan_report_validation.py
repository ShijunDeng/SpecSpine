"""Validation helpers for coverage plan report building."""

from __future__ import annotations

from pathlib import Path

from specspine.features import validate_feature_slug

__all__ = [
    "validate_coverage_plan_inputs",
]


def validate_coverage_plan_inputs(
    resolved_root: Path,
    *,
    limit: int | None = None,
    feature_filter: str | None = None,
) -> None:
    """Validate coverage plan inputs without changing behavior."""
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")
    if feature_filter is not None:
        validate_feature_slug(feature_filter)
