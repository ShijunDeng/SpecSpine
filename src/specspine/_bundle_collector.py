from __future__ import annotations

from pathlib import Path

from .features import (
    list_feature_bundles,
    InvalidFeatureSlug,
)
from .harness_coverage_models import HarnessDimensionCoverage
from .harness_coverage_sensors import _evaluate_dimensions

__all__ = [
    "_collect_bundle_dimensions",
]


def _collect_bundle_dimensions(
    resolved_root: Path,
) -> list[HarnessDimensionCoverage]:
    all_dimensions: list[HarnessDimensionCoverage] = []
    bundles = list_feature_bundles(resolved_root)
    for bundle in bundles:
        slug = str(bundle["slug"])
        try:
            bundle_dimensions = _evaluate_dimensions(slug, resolved_root)
            all_dimensions.extend(bundle_dimensions)
        except (InvalidFeatureSlug, OSError):
            continue
    return all_dimensions
