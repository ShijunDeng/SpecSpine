from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureBundleNotFoundError,
    FeatureHandoffReport,
    _empty_trace_summary,
    read_feature_metadata,
    validate_feature_slug,
)
from .feature_bundle_io_status_single import get_feature_status
from .feature_handoff_actions import _handoff_next_actions
from .feature_handoff_commands import _recommended_handoff_commands
from .feature_handoff_core_quality import _parse_release_readiness_from_file
from .feature_handoff_core_trace import _build_trace_with_fallback
from .feature_ready import build_feature_ready_report
from .feature_tasks import build_feature_tasks_report


def build_feature_handoff_report(
    root: Path,
    slug: str,
    *,
    require_coverage: bool = False,
) -> FeatureHandoffReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    status_report = get_feature_status(resolved_root, slug)
    metadata = read_feature_metadata(resolved_root, slug)
    has_native_files = any(file["exists"] for file in status_report.files.values())

    trace_report = _build_trace_with_fallback(resolved_root, slug, status_report)

    try:
        tasks_report = build_feature_tasks_report(resolved_root, slug)
        task_summary = tasks_report.summary
    except FeatureBundleNotFoundError:
        task_summary = {"done": 0, "open": 0, "total": 0}

    ready_report = build_feature_ready_report(
        resolved_root,
        slug,
        require_coverage=require_coverage,
    )

    release_readiness = _parse_release_readiness_from_file(resolved_root, slug)

    next_actions = _handoff_next_actions(
        slug=slug,
        has_native_files=has_native_files,
        missing_files=trace_report.missing_files,
        gaps=trace_report.gaps,
        tasks=trace_report.tasks,
        blocking_checks=ready_report.blocking_checks,
        ready=ready_report.ready,
    )

    return FeatureHandoffReport(
        feature_id=slug,
        status=trace_report.status,
        ready=ready_report.ready,
        sources=trace_report.sources,
        missing_files=trace_report.missing_files,
        gaps=trace_report.gaps,
        blocking_checks=ready_report.blocking_checks,
        acceptance_criteria=trace_report.acceptance_criteria,
        tasks=trace_report.tasks,
        quality_checks=trace_report.quality_checks,
        test_plan=trace_report.test_plan,
        release_readiness=release_readiness,
        trace_summary=trace_report.summary if has_native_files else _empty_trace_summary(),
        ready_summary=ready_report.summary,
        task_summary=task_summary,
        recommended_commands=_recommended_handoff_commands(slug),
        next_actions=next_actions,
        has_native_files=has_native_files,
        metadata=metadata,
    )


__all__ = [
    "FeatureHandoffReport",
    "build_feature_handoff_report",
]
