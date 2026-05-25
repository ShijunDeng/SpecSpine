from __future__ import annotations

from pathlib import Path
from typing import Any

from .harness_coverage_models import (
    DIMENSION_SENSOR_MAP,
    GOVERNED_DIMENSIONS,
    HarnessDimensionCoverage,
)
from .harness_coverage_sensors import _evaluate_dimensions

__all__ = [
    "_evaluate_single_feature_dimensions",
]


def _evaluate_single_feature_dimensions(
    feature_filter: str,
    resolved_root: Path,
) -> tuple[list[HarnessDimensionCoverage], str]:
    from .features import validate_feature_slug
    slug = validate_feature_slug(feature_filter)
    dimensions = _evaluate_dimensions(slug, resolved_root)
    return dimensions, slug
