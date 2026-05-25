from __future__ import annotations

from .harness_coverage_models import (
    DIMENSION_SENSOR_MAP,
    MATURITY_LABELS,
    HarnessDimensionCoverage,
)
from ._metrics_maturity import _compute_maturity_score

__all__ = [
    "_generate_improvement_plan",
]


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
