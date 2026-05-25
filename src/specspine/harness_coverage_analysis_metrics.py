from __future__ import annotations

from typing import Any

from .harness_coverage_models import (
    DIMENSION_SENSOR_MAP,
    MATURITY_LABELS,
    HarnessDimensionCoverage,
)

__all__ = [
    "_detect_blind_spots",
    "_detect_redundancy",
    "_compute_maturity_score",
    "_generate_improvement_plan",
]


def _detect_blind_spots(dimensions: list[HarnessDimensionCoverage]) -> list[str]:
    return [
        d.dimension_name
        for d in dimensions
        if d.sensor_count == 0
    ]


def _detect_redundancy(dimensions: list[HarnessDimensionCoverage]) -> list[dict[str, Any]]:
    redundancy_info: list[dict[str, Any]] = []
    for d in dimensions:
        if d.redundant_sensors:
            redundancy_info.append({
                "dimension": d.dimension_name,
                "redundant_sensors": list(d.redundant_sensors),
            })
    return redundancy_info


def _compute_maturity_score(dimensions: list[HarnessDimensionCoverage]) -> int:
    if not dimensions:
        return 0

    total_sensors = sum(d.sensor_count for d in dimensions)
    if total_sensors == 0:
        return 0

    pass_sensors = sum(d.pass_count for d in dimensions)
    overall_coverage = pass_sensors / total_sensors * 100

    dimensions_with_sensors = sum(1 for d in dimensions if d.sensor_count > 0)
    dimensions_fully_covered = sum(1 for d in dimensions if d.coverage_pct >= 100.0)
    dimensions_no_blind = sum(1 for d in dimensions if d.missing_sensors == ())

    if dimensions_fully_covered == len(dimensions) and dimensions_no_blind == len(dimensions):
        return 5

    if dimensions_fully_covered >= len(dimensions) * 0.75 and overall_coverage >= 90:
        return 4

    if dimensions_with_sensors >= len(dimensions) * 0.75 and overall_coverage >= 70:
        return 3

    if dimensions_with_sensors >= len(dimensions) * 0.5 and overall_coverage >= 50:
        return 2

    if total_sensors > 0:
        return 1

    return 0


def _generate_improvement_plan(
    dimensions: list[HarnessDimensionCoverage],
    blind_spots: list[str],
) -> list[str]:
    plan: list[str] = []

    for spot in blind_spots:
        sensor_name = DIMENSION_SENSOR_MAP.get(spot, spot)
        plan.append(f"Add {sensor_name} sensor to cover {spot} dimension.")

    for d in sorted(dimensions, key=lambda x: x.coverage_pct):
        if d.coverage_pct > 0 and d.coverage_pct < 100:
            plan.append(
                f"Improve {d.dimension_name} dimension coverage from "
                f"{d.coverage_pct}% to 100%."
            )
        if d.redundant_sensors:
            plan.append(
                f"Review redundant sensors in {d.dimension_name}: "
                f"{', '.join(d.redundant_sensors)}."
            )

    maturity = _compute_maturity_score(dimensions)
    if maturity < 3:
        plan.append(
            f"Current harness maturity is {maturity} ({MATURITY_LABELS[maturity]}); "
            f"target level 3 (defined) or higher."
        )

    return plan
