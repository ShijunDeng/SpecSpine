from __future__ import annotations

from .analysis_models import (
    FeatureAnalysis,
    _PendingIssue,
)
from .analysis_traceability import (
    _missing_files,
    _source_files,
    _trace_gap_issues,
    _readiness_issues,
    _ac_traceability_issues,
    _task_traceability_issues,
    _criterion_quality_issues,
)
from .analysis_build_commands import _dedupe_commands
from ._analysis_assembly_coverage import FeatureAnalysisData

__all__ = [
    "collect_feature_issues",
    "build_feature_analysis_result",
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


def build_feature_analysis_result(
    feature: dict[str, object],
    data: FeatureAnalysisData,
    pending_issues: list[_PendingIssue],
) -> tuple[FeatureAnalysis, list[_PendingIssue]]:
    metrics: dict[str, int | bool] = {
        "acceptance_criteria_total": len(data.trace_report.acceptance_criteria),
        "coverage_links_total": len(data.coverage_links),
        "covered_acceptance_criteria": len(data.covered_ids),
        "quality_checks_total": len(data.trace_report.quality_checks),
        "ready": data.ready_report.ready,
        "readiness_blocking_checks": len(data.ready_report.blocking_checks),
        "tasks_total": len(data.trace_report.tasks),
        "test_plan_total": len(data.trace_report.test_plan),
    }
    recommended_commands = _dedupe_commands(
        [
            command
            for issue in pending_issues
            for command in (
                [issue.recommended_command] if issue.recommended_command else []
            )
        ]
        or ["specspine validate . --fusion --features --json"]
    )
    return (
        FeatureAnalysis(
            feature_id=data.slug,
            status=data.trace_report.status,
            ready=data.ready_report.ready,
            source_files=_source_files(feature, data.slug),
            missing_files=_missing_files(feature, data.slug),
            metrics=metrics,
            issues=(),
            recommended_commands=recommended_commands,
        ),
        pending_issues,
    )
