from __future__ import annotations

from ..features import (
    FeatureTask,
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
)
from ..analysis_models import _PendingIssue
from ._ac_traceability_task_refs import _ac_traceability_task_issues
from ._ac_traceability_coverage import _ac_traceability_coverage_issues

__all__ = [
    "_ac_traceability_issues",
]


def _ac_traceability_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    tasks: tuple[FeatureTask, ...],
    coverage_links: tuple[FeatureTestCoverageLink, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    issues.extend(_ac_traceability_task_issues(slug, acceptance_criteria, tasks))
    issues.extend(_ac_traceability_coverage_issues(slug, acceptance_criteria, coverage_links))
    return issues
