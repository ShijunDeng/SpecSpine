from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureStatusReport,
    FeatureTraceReport,
    validate_feature_slug,
    _relative_feature_paths,
    get_feature_status,
)
from ._trace_file_loading import _load_feature_contents
from ._trace_parsing import _parse_trace_artifacts
from ._trace_gap_detection import _detect_trace_gaps

__all__ = [
    "build_feature_trace_report",
]


def build_feature_trace_report(root: Path, slug: str) -> FeatureTraceReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    relative_paths = _relative_feature_paths(slug)

    contents, missing_files, sources = _load_feature_contents(resolved_root, slug)

    spec_file = relative_paths["spec"]
    execution_file = relative_paths["execution"]
    quality_file = relative_paths["quality"]

    acceptance_criteria, tasks, quality_checks, test_plan = _parse_trace_artifacts(
        contents, spec_file, execution_file, quality_file
    )

    gaps = _detect_trace_gaps(
        missing_files,
        spec_file,
        execution_file,
        quality_file,
        acceptance_criteria,
        tasks,
        quality_checks,
        test_plan,
    )

    status_report = get_feature_status(resolved_root, slug)

    return FeatureTraceReport(
        feature_id=slug,
        status=status_report.status or "unknown",
        sources=sources,
        missing_files=tuple(missing_files),
        acceptance_criteria=acceptance_criteria,
        tasks=tasks,
        quality_checks=quality_checks,
        test_plan=test_plan,
        gaps=tuple(gaps),
    )
