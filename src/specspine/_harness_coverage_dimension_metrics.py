from __future__ import annotations

from .harness import HarnessFeedbackSensor
from .harness_coverage_models import (
    DIMENSION_SENSOR_MAP,
    GOVERNED_DIMENSIONS,
    HarnessDimensionCoverage,
)

__all__ = [
    "_compute_dimension_metrics",
]


def _find_redundant_sensors(
    dim_sensors: list[HarnessFeedbackSensor],
) -> tuple[str, ...]:
    ac_sets = [frozenset(s.ac_ids) for s in dim_sensors]
    redundant: list[str] = []
    for i in range(len(dim_sensors)):
        for j in range(i + 1, len(dim_sensors)):
            if ac_sets[i] & ac_sets[j]:
                redundant.append(dim_sensors[i].name)
                redundant.append(dim_sensors[j].name)
    return tuple(sorted(set(redundant)))


def _compute_dimension_metrics(
    all_sensors_by_name: dict[str, list[HarnessFeedbackSensor]],
) -> list[HarnessDimensionCoverage]:
    dimensions: list[HarnessDimensionCoverage] = []

    for dim in GOVERNED_DIMENSIONS:
        sensor_name = DIMENSION_SENSOR_MAP[dim]
        dim_sensors = all_sensors_by_name.get(sensor_name, [])
        sensor_count = len(dim_sensors)
        pass_count = sum(1 for s in dim_sensors if s.status == "pass")
        coverage_pct = (pass_count / sensor_count * 100) if sensor_count > 0 else 0.0

        missing_sensors: tuple[str, ...] = ()
        if sensor_count == 0:
            missing_sensors = (sensor_name,)

        redundant_sensors: tuple[str, ...] = ()
        if sensor_count > 1:
            redundant_sensors = _find_redundant_sensors(dim_sensors)

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
