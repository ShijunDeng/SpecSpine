from __future__ import annotations

from ..features import (
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
)
from ..analysis_traceability_ac_helpers import (
    _coverage_ac_id,
)

__all__ = [
    "_build_coverage_refs",
    "_build_covered_refs",
]


def _build_coverage_refs(
    coverage_links: tuple[FeatureTestCoverageLink, ...],
) -> set[str]:
    return {_coverage_ac_id(link) for link in coverage_links}


def _build_covered_refs(
    coverage_links: tuple[FeatureTestCoverageLink, ...],
) -> set[str]:
    return {
        _coverage_ac_id(link)
        for link in coverage_links
        if link.done and link.target_exists
    }
