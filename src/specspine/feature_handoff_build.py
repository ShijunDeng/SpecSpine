from __future__ import annotations

import json
from pathlib import Path

from .feature_bundle import (
    FeatureBundleNotFoundError,
    FeatureHandoffReport,
    FeatureMetadata,
    FeatureTraceChecklistItem,
    FeatureTraceReport,
    _relative_feature_paths,
    _trace_gap,
    feature_bundle_paths,
    get_feature_status,
    parse_release_readiness,
    read_feature_metadata,
    validate_feature_slug,
)
from .feature_ready import build_feature_ready_report
from .feature_tasks import build_feature_tasks_report
from .feature_trace import build_feature_trace_report, _empty_trace_summary, _feature_sources_from_status
from .feature_handoff_actions import _handoff_next_actions

__all__ = [
    "FeatureHandoffReport",
    "build_feature_handoff_report",
]


def _recommended_handoff_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature handoff {slug} . --json",
        f"specspine feature tasks {slug} . --json",
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature ready {slug} . --json",
        f"specspine feature pr {slug} . --json",
        "specspine validate . --fusion --features",
    )


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

    try:
        trace_report = build_feature_trace_report(resolved_root, slug)
    except FeatureBundleNotFoundError:
        missing_files = status_report.missing_files
        gaps = tuple(
            _trace_gap(
                "missing_file",
                relative_path,
                f"Missing native feature file: {relative_path}",
            )
            for relative_path in missing_files
        )
        trace_report = FeatureTraceReport(
            feature_id=slug,
            status=status_report.status or "unknown",
            sources=_feature_sources_from_status(status_report),
            missing_files=missing_files,
            acceptance_criteria=(),
            tasks=(),
            quality_checks=(),
            test_plan=(),
            gaps=gaps,
        )

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

    relative_paths = _relative_feature_paths(slug)
    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    release_readiness: tuple[FeatureTraceChecklistItem, ...] = ()
    if quality_path.exists():
        release_readiness = parse_release_readiness(
            quality_path.read_text(encoding="utf-8"),
            source_file=relative_paths["quality"],
        )

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
