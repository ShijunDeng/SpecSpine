from __future__ import annotations

from pathlib import Path

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
from ._analysis_build_feature_coverage import (
    _compute_coverage_links,
    _compute_coverage_ids,
)

__all__ = [
    "_build_feature_analysis",
]


def _build_feature_analysis(
    root: Path,
    feature: dict[str, object],
) -> tuple[FeatureAnalysis, list[_PendingIssue]]:
    from .features import (
        FeatureBundleNotFoundError,
        build_feature_ready_report,
        build_feature_trace_report,
    )
    from .analysis_build_feature_missing import _build_missing_feature_analysis

    slug = str(feature["slug"])
    try:
        trace_report = build_feature_trace_report(root, slug)
    except FeatureBundleNotFoundError:
        return _build_missing_feature_analysis(root, slug)

    ready_report = build_feature_ready_report(root, slug, require_coverage=True)
    coverage_links = _compute_coverage_links(root, slug)
    known_ids = {criterion.id for criterion in trace_report.acceptance_criteria}
    covered_ids = _compute_coverage_ids(coverage_links, known_ids)

    pending_issues: list[_PendingIssue] = []
    pending_issues.extend(_trace_gap_issues(slug, trace_report))
    pending_issues.extend(_readiness_issues(slug, ready_report.blocking_checks))
    pending_issues.extend(
        _ac_traceability_issues(
            slug,
            trace_report.acceptance_criteria,
            trace_report.tasks,
            coverage_links,
        )
    )
    pending_issues.extend(_task_traceability_issues(slug, trace_report.tasks))
    pending_issues.extend(_criterion_quality_issues(slug, trace_report.acceptance_criteria))

    metrics: dict[str, int | bool] = {
        "acceptance_criteria_total": len(trace_report.acceptance_criteria),
        "coverage_links_total": len(coverage_links),
        "covered_acceptance_criteria": len(covered_ids),
        "quality_checks_total": len(trace_report.quality_checks),
        "ready": ready_report.ready,
        "readiness_blocking_checks": len(ready_report.blocking_checks),
        "tasks_total": len(trace_report.tasks),
        "test_plan_total": len(trace_report.test_plan),
    }
    recommended_commands = _dedupe_commands(
        [
            command
            for issue in pending_issues
            for command in ([issue.recommended_command] if issue.recommended_command else [])
        ]
        or ["specspine validate . --fusion --features --json"]
    )
    return (
        FeatureAnalysis(
            feature_id=slug,
            status=trace_report.status,
            ready=ready_report.ready,
            source_files=_source_files(feature, slug),
            missing_files=_missing_files(feature, slug),
            metrics=metrics,
            issues=(),
            recommended_commands=recommended_commands,
        ),
        pending_issues,
    )
