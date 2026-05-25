from __future__ import annotations

import json
from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    FeatureReadyCheck,
    FeatureReadyReport,
    FeatureTraceChecklistItem,
    FeatureTestCoverageLink,
    FeatureTraceTestPlanItem,
    _relative_feature_paths,
    _trace_gap,
    feature_bundle_paths,
    get_feature_status,
    parse_release_readiness,
    parse_test_coverage,
    validate_feature_slug,
)
from .feature_trace import build_feature_trace_report
from .feature_ready_checks import _ready_check, _checklist_ready_message
from .feature_ready_coverage import _coverage_ready_message

__all__ = [
    "FeatureReadyCheck",
    "FeatureReadyReport",
    "build_feature_ready_report",
    "render_feature_ready_json",
    "render_feature_ready_text",
]


def build_feature_ready_report(
    root: Path,
    slug: str,
    *,
    require_coverage: bool = False,
    policy_applied: bool = False,
    coverage_required_by_policy: bool = False,
    policy_source: str | None = None,
) -> FeatureReadyReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    relative_paths = _relative_feature_paths(slug)
    status_report = get_feature_status(resolved_root, slug)

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
        status = status_report.status or "unknown"
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

    if require_coverage:
        passed, message = _coverage_ready_message(
            acceptance_criteria,
            test_coverage,
        )
        checks.append(_ready_check("feature.test_coverage", passed, message))

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


def render_feature_ready_json(report: FeatureReadyReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_ready_text(report: FeatureReadyReport) -> str:
    summary = report.summary
    lines = [
        f"Feature readiness: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        (
            "Summary: "
            f"pass={summary['pass']} "
            f"fail={summary['fail']} "
            f"total={summary['total']}"
        ),
        "Blocking checks:",
    ]
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    return "\n".join(lines) + "\n"
