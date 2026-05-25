from __future__ import annotations

from pathlib import Path

__all__ = [
    "_gather_trace_data",
    "_gather_quality_data",
    "_gather_status_data",
    "_build_file_checks",
    "_build_trace_checks",
    "_build_coverage_check",
    "build_feature_ready_report",
]


def _gather_status_data(
    resolved_root: Path,
    slug: str,
) -> tuple:
    from .feature_bundle import (
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
    from .feature_bundle import (
        FEATURE_FILE_PATHS,
        FeatureBundleNotFoundError,
        _trace_gap,
    )
    from .feature_trace import build_feature_trace_report

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
    from .feature_bundle import (
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


def _build_file_checks(
    missing_files: tuple[str, ...],
    status_report,
    status: str,
) -> list:
    from .feature_bundle import FeatureReadyCheck
    from .feature_ready_checks import _ready_check

    checks: list[FeatureReadyCheck] = []

    checks.append(
        _ready_check(
            "feature.bundle_files",
            not missing_files,
            (
                "All native feature peer files are present."
                if not missing_files
                else "Missing native feature peer files: "
                + ", ".join(missing_files)
            ),
        )
    )

    checks.append(
        _ready_check(
            "feature.status_consistency",
            status_report.consistent,
            (
                f"Peer-file status is consistent: {status_report.status}."
                if status_report.consistent
                else "Peer-file statuses are missing or inconsistent."
            ),
        )
    )

    lifecycle_ready = status in {"implemented", "validated"}
    checks.append(
        _ready_check(
            "feature.lifecycle_status",
            lifecycle_ready,
            (
                f"Lifecycle status is releasable: {status}."
                if lifecycle_ready
                else "Lifecycle status must be implemented or validated; "
                f"found {status}."
            ),
        )
    )

    return checks


def _build_trace_checks(
    gaps: tuple,
    acceptance_criteria: tuple,
    tasks: tuple,
    quality_checks: tuple,
    test_plan: tuple,
    release_readiness: tuple,
) -> list:
    from .feature_bundle import FeatureReadyCheck
    from .feature_ready_checks import _ready_check, _checklist_ready_message

    checks: list[FeatureReadyCheck] = []

    gap_ids = sorted({gap["id"] for gap in gaps})
    checks.append(
        _ready_check(
            "feature.trace_gaps",
            not gaps,
            (
                "Trace gaps are empty."
                if not gaps
                else "Trace gaps present: " + ", ".join(gap_ids)
            ),
        )
    )

    for check_id, label, items in (
        ("feature.acceptance_criteria", "acceptance criteria", acceptance_criteria),
        ("feature.tasks", "tasks", tasks),
        ("feature.required_checks", "required checks", quality_checks),
    ):
        passed, message = _checklist_ready_message(label=label, items=items)
        checks.append(_ready_check(check_id, passed, message))

    checks.append(
        _ready_check(
            "feature.test_plan",
            bool(test_plan),
            (
                f"Test plan has {len(test_plan)} non-empty line(s)."
                if test_plan
                else "No non-empty test plan content found."
            ),
        )
    )

    passed, message = _checklist_ready_message(
        label="release readiness",
        items=release_readiness,
    )
    checks.append(_ready_check("feature.release_readiness", passed, message))

    return checks


def _build_coverage_check(
    acceptance_criteria: tuple,
    test_coverage: tuple,
):
    from .feature_bundle import FeatureReadyCheck
    from .feature_ready_checks import _ready_check
    from .feature_ready_coverage import _coverage_ready_message

    passed, message = _coverage_ready_message(
        acceptance_criteria,
        test_coverage,
    )
    return _ready_check("feature.test_coverage", passed, message)


def build_feature_ready_report(
    root: Path,
    slug: str,
    *,
    require_coverage: bool = False,
    policy_applied: bool = False,
    coverage_required_by_policy: bool = False,
    policy_source: str | None = None,
):
    from .feature_bundle import FeatureReadyReport

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
