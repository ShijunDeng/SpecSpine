from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .features import (
    FeatureBundleNotFoundError,
    FeatureReadyReport,
    FeatureStatusReport,
    FeatureTasksReport,
    FeatureTestsReport,
    FeatureTraceReport,
    build_feature_ready_report,
    build_feature_tasks_report,
    build_feature_tests_report,
    build_feature_trace_report,
    feature_bundle_paths,
    get_feature_status,
    read_feature_metadata,
    validate_feature_slug,
)

from .archive_helpers import (
    _archive_recommended_commands,
    _archive_safety_notes,
    _coverage_section_exists,
    _default_archive_id,
    _source_and_missing_files,
    validate_archive_id,
)
from .archive_models import (
    ARCHIVE_ID_RE,
    TEST_COVERAGE_HEADING_RE,
    FeatureArchiveArtifactExistsError,
    FeatureArchivePackage,
    FeatureArchiveReport,
    InvalidArchiveId,
)
from .archive_render import (
    feature_archive_report_with_package,
    render_feature_archive_json,
    render_feature_archive_text,
)
from .archive_writer import (
    _archive_write_targets,
    _source_snapshot_path,
    write_feature_archive_package,
)


def build_feature_archive_report(
    root: Path,
    slug: str,
    *,
    archive_id: str | None = None,
) -> FeatureArchiveReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    resolved_archive_id = validate_archive_id(archive_id or _default_archive_id(slug))

    status_report = get_feature_status(resolved_root, slug)
    has_native_files = any(file["exists"] for file in status_report.files.values())
    if not has_native_files:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(feature_bundle_paths(resolved_root, slug).values()),
        )

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

    return FeatureArchiveReport(
        archive_id=resolved_archive_id,
        feature_id=slug,
        workspace_root=resolved_root,
        status=status_report.status or "unknown",
        ready=ready_report.ready,
        coverage_required=coverage_required,
        status_report=status_report,
        ready_report=ready_report,
        trace_report=trace_report,
        tasks_report=tasks_report,
        tests_report=tests_report,
        metadata=metadata,
        source_files=source_files,
        missing_files=missing_files,
        safety_notes=_archive_safety_notes(coverage_required),
        recommended_commands=_archive_recommended_commands(slug),
    )


__all__ = [
    "ARCHIVE_ID_RE",
    "TEST_COVERAGE_HEADING_RE",
    "InvalidArchiveId",
    "FeatureArchiveArtifactExistsError",
    "FeatureArchivePackage",
    "FeatureArchiveReport",
    "validate_archive_id",
    "_default_archive_id",
    "_coverage_section_exists",
    "_source_and_missing_files",
    "_archive_safety_notes",
    "_archive_recommended_commands",
    "build_feature_archive_report",
    "render_feature_archive_json",
    "feature_archive_report_with_package",
    "render_feature_archive_text",
    "_source_snapshot_path",
    "_archive_write_targets",
    "write_feature_archive_package",
]
