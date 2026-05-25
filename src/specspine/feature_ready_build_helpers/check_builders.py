from __future__ import annotations

__all__ = [
    "_build_file_checks",
    "_build_trace_checks",
    "_build_coverage_check",
]


def _build_file_checks(
    missing_files: tuple[str, ...],
    status_report,
    status: str,
) -> list:
    from ..feature_bundle import FeatureReadyCheck
    from ..feature_ready_checks import _ready_check

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
    from ..feature_bundle import FeatureReadyCheck
    from ..feature_ready_checks import _ready_check, _checklist_ready_message

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
    from ..feature_bundle import FeatureReadyCheck
    from ..feature_ready_checks import _ready_check
    from ..feature_ready_coverage import _coverage_ready_message

    passed, message = _coverage_ready_message(
        acceptance_criteria,
        test_coverage,
    )
    return _ready_check("feature.test_coverage", passed, message)
