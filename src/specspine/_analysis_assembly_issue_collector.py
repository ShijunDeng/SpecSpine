from __future__ import annotations

from ._analysis_assembly_coverage import FeatureAnalysisData
from .analysis_models import _PendingIssue
from .analysis_traceability import (
    _trace_gap_issues,
    _readiness_issues,
    _ac_traceability_issues,
    _task_traceability_issues,
    _criterion_quality_issues,
)

__all__ = [
    "collect_feature_issues",
]


def collect_feature_issues(
    data: FeatureAnalysisData,
) -> list[_PendingIssue]:
    pending_issues: list[_PendingIssue] = []
    pending_issues.extend(_trace_gap_issues(data.slug, data.trace_report))
    pending_issues.extend(
        _readiness_issues(data.slug, data.ready_report.blocking_checks)
    )
    pending_issues.extend(
        _ac_traceability_issues(
            data.slug,
            data.trace_report.acceptance_criteria,
            data.trace_report.tasks,
            data.coverage_links,
        )
    )
    pending_issues.extend(
        _task_traceability_issues(data.slug, data.trace_report.tasks)
    )
    pending_issues.extend(
        _criterion_quality_issues(data.slug, data.trace_report.acceptance_criteria)
    )
    return pending_issues
