from __future__ import annotations

from pathlib import Path

from .features import (
    build_feature_ready_report,
    build_feature_trace_report,
)
from ._analysis_build_feature_coverage import (
    _compute_coverage_links,
    _compute_coverage_ids,
)

__all__ = [
    "FeatureAnalysisData",
    "gather_feature_analysis_data",
]


class FeatureAnalysisData:
    def __init__(
        self,
        slug: str,
        trace_report,
        ready_report,
        coverage_links: list,
        covered_ids: set[str],
    ) -> None:
        self.slug = slug
        self.trace_report = trace_report
        self.ready_report = ready_report
        self.coverage_links = coverage_links
        self.covered_ids = covered_ids


def gather_feature_analysis_data(
    root: Path, slug: str
) -> FeatureAnalysisData:
    trace_report = build_feature_trace_report(root, slug)
    ready_report = build_feature_ready_report(root, slug, require_coverage=True)
    coverage_links = _compute_coverage_links(root, slug)
    known_ids = {criterion.id for criterion in trace_report.acceptance_criteria}
    covered_ids = _compute_coverage_ids(coverage_links, known_ids)

    return FeatureAnalysisData(
        slug=slug,
        trace_report=trace_report,
        ready_report=ready_report,
        coverage_links=coverage_links,
        covered_ids=covered_ids,
    )
