from __future__ import annotations

from pathlib import Path

from .features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
)
from .harness_coverage_models import (
    DIMENSION_SENSOR_MAP,
    GOVERNED_DIMENSIONS,
    HarnessDimensionCoverage,
)
from .harness import HarnessFeedbackSensor

__all__ = [
    "_evaluate_dimensions",
]


def _evaluate_dimensions(slug: str, root: Path) -> list[HarnessDimensionCoverage]:
    resolved_root = root.expanduser().resolve()
    dimensions: list[HarnessDimensionCoverage] = []

    all_sensors_by_name: dict[str, list[HarnessFeedbackSensor]] = {}
    try:
        from .harness import _run_computational_sensors, _run_inferential_sensors
        computational = _run_computational_sensors(slug, resolved_root)
        inferential = _run_inferential_sensors(slug, resolved_root)
        all_s = computational + inferential
        for s in all_s:
            all_sensors_by_name.setdefault(s.name, []).append(s)
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        pass

    for dim in GOVERNED_DIMENSIONS:
        sensor_name = DIMENSION_SENSOR_MAP[dim]
        dim_sensors = all_sensors_by_name.get(sensor_name, [])
        sensor_count = len(dim_sensors)
        pass_count = sum(1 for s in dim_sensors if s.status == "pass")
        coverage_pct = (pass_count / sensor_count * 100) if sensor_count > 0 else 0.0

        missing_sensors: tuple[str, ...] = ()
        if sensor_count == 0:
            missing_sensors = (sensor_name,)

        redundant: list[str] = []
        if sensor_count > 1:
            ac_sets = [frozenset(s.ac_ids) for s in dim_sensors]
            for i in range(len(dim_sensors)):
                for j in range(i + 1, len(dim_sensors)):
                    if ac_sets[i] & ac_sets[j]:
                        redundant.append(dim_sensors[i].name)
                        redundant.append(dim_sensors[j].name)
            redundant_sensors = tuple(sorted(set(redundant)))
        else:
            redundant_sensors = ()

        dimensions.append(
            HarnessDimensionCoverage(
                dimension_name=dim,
                sensor_count=sensor_count,
                pass_count=pass_count,
                coverage_pct=round(coverage_pct, 2),
                missing_sensors=missing_sensors,
                redundant_sensors=redundant_sensors,
            )
        )

    return dimensions
