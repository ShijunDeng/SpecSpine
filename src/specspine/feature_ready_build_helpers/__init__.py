from __future__ import annotations

from pathlib import Path

from .data_gathering import (
    _gather_status_data,
    _gather_trace_data,
    _gather_quality_data,
)
from .check_builders import (
    _build_file_checks,
    _build_trace_checks,
    _build_coverage_check,
)

__all__ = [
    "_gather_trace_data",
    "_gather_quality_data",
    "_gather_status_data",
    "_build_file_checks",
    "_build_trace_checks",
    "_build_coverage_check",
    "build_feature_ready_report",
]


def build_feature_ready_report(
    root: Path,
    slug: str,
    *,
    require_coverage: bool = False,
    policy_applied: bool = False,
    coverage_required_by_policy: bool = False,
    policy_source: str | None = None,
):
    from ..feature_bundle import FeatureReadyReport

    resolved_root = root.expanduser().resolve()

    relative_paths, status_report = _gather_status_data(resolved_root, slug)

    (
        status,
        missing_files,
        gaps,
        acceptance_criteria,
        tasks,
        quality_checks,
        test_plan,
    ) = _gather_trace_data(resolved_root, slug, relative_paths)

    release_readiness, test_coverage = _gather_quality_data(
        resolved_root, slug, relative_paths, require_coverage
    )

    checks = _build_file_checks(missing_files, status_report, status)
    checks += _build_trace_checks(
        gaps,
        acceptance_criteria,
        tasks,
        quality_checks,
        test_plan,
        release_readiness,
    )

    if require_coverage:
        checks.append(_build_coverage_check(acceptance_criteria, test_coverage))

    ready = all(check.status == "pass" for check in checks)
    return FeatureReadyReport(
        feature_id=slug,
        ready=ready,
        status=status,
        checks=tuple(checks),
        missing_files=missing_files,
        gaps=gaps,
        coverage_required=require_coverage,
        policy_applied=policy_applied,
        coverage_required_by_policy=coverage_required_by_policy,
        policy_source=policy_source,
    )
