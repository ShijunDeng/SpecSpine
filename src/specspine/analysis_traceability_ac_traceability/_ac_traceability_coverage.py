from __future__ import annotations

from ..features import (
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
)
from ..analysis_models import _PendingIssue
from ._coverage_link_processing import (
    _build_coverage_refs,
    _build_covered_refs,
)
from ._coverage_issue_detection import (
    _detect_missing_coverage_links,
    _detect_incomplete_coverage,
    _detect_unknown_criterion_links,
    _detect_missing_targets,
    _detect_open_links,
)

__all__ = [
    "_ac_traceability_coverage_issues",
]


def _ac_traceability_coverage_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    coverage_links: tuple[FeatureTestCoverageLink, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    coverage_refs = _build_coverage_refs(coverage_links)
    covered_refs = _build_covered_refs(coverage_links)
    known_ids = {criterion.id for criterion in acceptance_criteria}

    issues.extend(
        _detect_missing_coverage_links(slug, acceptance_criteria, coverage_refs)
    )
    issues.extend(
        _detect_incomplete_coverage(slug, acceptance_criteria, coverage_refs, covered_refs)
    )
    issues.extend(
        _detect_unknown_criterion_links(slug, coverage_links, known_ids)
    )
    issues.extend(
        _detect_missing_targets(slug, coverage_links)
    )
    issues.extend(
        _detect_open_links(slug, coverage_links, known_ids)
    )

    return issues
