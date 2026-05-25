from __future__ import annotations

from pathlib import Path

__all__ = [
    "_gather_status_data",
    "_gather_trace_data",
    "_gather_quality_data",
]


def _gather_status_data(
    resolved_root: Path,
    slug: str,
) -> tuple:
    from ..feature_bundle import (
        _relative_feature_paths,
        feature_bundle_paths,
        get_feature_status,
        validate_feature_slug,
    )
    slug = validate_feature_slug(slug)
    relative_paths = _relative_feature_paths(slug)
    status_report = get_feature_status(resolved_root, slug)
    return relative_paths, status_report


def _gather_trace_data(
    resolved_root: Path,
    slug: str,
    relative_paths: dict,
) -> tuple:
    from ..feature_bundle import (
        FEATURE_FILE_PATHS,
        FeatureBundleNotFoundError,
        _trace_gap,
    )
    from ..feature_trace import build_feature_trace_report

    try:
        trace_report = build_feature_trace_report(resolved_root, slug)
        status = trace_report.status
        missing_files = trace_report.missing_files
        gaps = trace_report.gaps
        acceptance_criteria = trace_report.acceptance_criteria
        tasks = trace_report.tasks
        quality_checks = trace_report.quality_checks
        test_plan = trace_report.test_plan
    except FeatureBundleNotFoundError:
        status = "unknown"
        missing_files = tuple(relative_paths[kind] for kind in FEATURE_FILE_PATHS)
        gaps = tuple(
            _trace_gap(
                "missing_file",
                relative_path,
                f"Missing native feature file: {relative_path}",
            )
            for relative_path in missing_files
        )
        acceptance_criteria = ()
        tasks = ()
        quality_checks = ()
        test_plan = ()
    return status, missing_files, gaps, acceptance_criteria, tasks, quality_checks, test_plan


def _gather_quality_data(
    resolved_root: Path,
    slug: str,
    relative_paths: dict,
    require_coverage: bool,
) -> tuple:
    from ..feature_bundle import (
        FeatureTraceChecklistItem,
        FeatureTestCoverageLink,
        feature_bundle_paths,
        parse_release_readiness,
        parse_test_coverage,
    )
    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    release_readiness: tuple[FeatureTraceChecklistItem, ...] = ()
    test_coverage: tuple[FeatureTestCoverageLink, ...] = ()
    if quality_path.exists():
        quality_content = quality_path.read_text(encoding="utf-8")
        release_readiness = parse_release_readiness(
            quality_content,
            source_file=relative_paths["quality"],
        )
        if require_coverage:
            test_coverage = parse_test_coverage(
                quality_content,
                source_file=relative_paths["quality"],
                root=resolved_root,
            )
    return release_readiness, test_coverage
