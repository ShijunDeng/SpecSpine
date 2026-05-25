from __future__ import annotations

from pathlib import Path

from ._harness_coverage_dimension_metrics import _compute_dimension_metrics
from ._harness_coverage_sensors_gather import _gather_sensors_by_name

__all__ = [
    "_evaluate_dimensions",
]


def _evaluate_dimensions(slug: str, root: Path) -> list:
    resolved_root = root.expanduser().resolve()
    all_sensors_by_name = _gather_sensors_by_name(slug, resolved_root)
    return _compute_dimension_metrics(all_sensors_by_name)
