from __future__ import annotations

from pathlib import Path
from typing import Any

from .features import (
    list_feature_bundles,
    InvalidFeatureSlug,
)
from .harness_coverage_models import (
    DIMENSION_SENSOR_MAP,
    GOVERNED_DIMENSIONS,
    HarnessDimensionCoverage,
)
from .harness_coverage_sensors import _evaluate_dimensions

__all__ = [
    "_aggregate_workspace_dimensions",
]


def _aggregate_workspace_dimensions(
    resolved_root: Path,
) -> tuple[list[HarnessDimensionCoverage], str]:
    all_dimensions: list[HarnessDimensionCoverage] = []
    bundles = list_feature_bundles(resolved_root)
    for bundle in bundles:
        slug = str(bundle["slug"])
        try:
            bundle_dimensions = _evaluate_dimensions(slug, resolved_root)
            all_dimensions.extend(bundle_dimensions)
        except (InvalidFeatureSlug, OSError):
            continue

    aggregated: dict[str, dict[str, Any]] = {}
    for d in all_dimensions:
        if d.dimension_name not in aggregated:
            aggregated[d.dimension_name] = {
                "dimension_name": d.dimension_name,
                "sensor_count": 0,
                "pass_count": 0,
                "missing_sensors": set(),
                "redundant_sensors": set(),
            }
        agg = aggregated[d.dimension_name]
        agg["sensor_count"] += d.sensor_count
        agg["pass_count"] += d.pass_count
        agg["missing_sensors"].update(d.missing_sensors)
        agg["redundant_sensors"].update(d.redundant_sensors)

    dimensions: list[HarnessDimensionCoverage] = []
    for dim in GOVERNED_DIMENSIONS:
        if dim in aggregated:
            agg = aggregated[dim]
            total = agg["sensor_count"]
            passed = agg["pass_count"]
            pct = (passed / total * 100) if total > 0 else 0.0
            dimensions.append(
                HarnessDimensionCoverage(
                    dimension_name=dim,
                    sensor_count=total,
                    pass_count=passed,
                    coverage_pct=round(pct, 2),
                    missing_sensors=tuple(sorted(agg["missing_sensors"])),
                    redundant_sensors=tuple(sorted(agg["redundant_sensors"])),
                )
            )
        else:
            dimensions.append(
                HarnessDimensionCoverage(
                    dimension_name=dim,
                    sensor_count=0,
                    pass_count=0,
                    coverage_pct=0.0,
                    missing_sensors=(DIMENSION_SENSOR_MAP[dim],),
                    redundant_sensors=(),
                )
            )

    return dimensions, "workspace"
