from __future__ import annotations

from pathlib import Path


def _gather_trace_data(
    resolved_root: Path,
    slug: str,
    relative_paths: dict,
) -> tuple:
    from ...feature_bundle import (
        FEATURE_FILE_PATHS,
        FeatureBundleNotFoundError,
        _trace_gap,
    )
    from ...feature_trace import build_feature_trace_report

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


__all__ = [
    "_gather_trace_data",
]
