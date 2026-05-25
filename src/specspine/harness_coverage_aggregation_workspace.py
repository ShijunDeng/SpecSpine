from __future__ import annotations

from pathlib import Path

from ._bundle_collector import (
    _collect_bundle_dimensions,
)
from ._dimension_aggregator import (
    _aggregate_dimensions,
)
from .harness_coverage_models import HarnessDimensionCoverage

__all__ = [
    "_aggregate_workspace_dimensions",
]


def _aggregate_workspace_dimensions(
    resolved_root: Path,
) -> tuple[list[HarnessDimensionCoverage], str]:
    all_dimensions = _collect_bundle_dimensions(resolved_root)
    dimensions = _aggregate_dimensions(all_dimensions)
    return dimensions, "workspace"
