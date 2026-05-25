from __future__ import annotations

from pathlib import Path

from specspine.features import (
    build_feature_ready_report,
    build_feature_tasks_report,
    build_feature_tests_report,
    build_feature_trace_report,
    read_feature_metadata,
)

from specspine.archive_helpers import (
    _coverage_section_exists,
    _source_and_missing_files,
)

__all__ = [
    "collect_archive_evidence",
]


def collect_archive_evidence(
    resolved_root: Path,
    slug: str,
    status_report,
) -> dict[str, object]:
    coverage_required = _coverage_section_exists(resolved_root, slug)
    ready_report = build_feature_ready_report(
        resolved_root,
        slug,
        require_coverage=coverage_required,
    )
    trace_report = build_feature_trace_report(resolved_root, slug)
    tasks_report = build_feature_tasks_report(resolved_root, slug)
    tests_report = build_feature_tests_report(resolved_root, slug)
    metadata = read_feature_metadata(resolved_root, slug).as_dict()
    source_files, missing_files = _source_and_missing_files(status_report)

    return {
        "coverage_required": coverage_required,
        "ready_report": ready_report,
        "trace_report": trace_report,
        "tasks_report": tasks_report,
        "tests_report": tests_report,
        "metadata": metadata,
        "source_files": source_files,
        "missing_files": missing_files,
    }
