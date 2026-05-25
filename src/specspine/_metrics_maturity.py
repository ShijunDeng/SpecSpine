from __future__ import annotations

from .harness_coverage_models import HarnessDimensionCoverage

__all__ = [
    "_compute_maturity_score",
]


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
