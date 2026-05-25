from __future__ import annotations

from .consistency_models import (
    ConsistencyCheck,
    DOCUMENTATION_GLOBS,
    IMPLEMENTATION_GLOBS,
    TEST_GLOBS,
)

__all__ = [
    "_check",
    "_feature_checks",
]


def _check(
    check_id: str,
    status: str,
    message: str,
) -> ConsistencyCheck:
    return ConsistencyCheck(id=check_id, status=status, message=message)


def _feature_checks(
    *,
    source_files: tuple[str, ...],
    missing_files: tuple[str, ...],
    implementation_references: tuple,
    test_references: tuple,
    documentation_references: tuple,
    changed_references: tuple,
    changed_files: tuple[str, ...],
) -> tuple[ConsistencyCheck, ...]:
    checks = [
        _check(
            "feature.bundle_files",
            "pass" if source_files and not missing_files else "fail",
            "Feature has all native peer files."
            if source_files and not missing_files
            else "Feature is missing one or more native peer files.",
        ),
        _check(
            "feature.implementation_references",
            "pass" if implementation_references else "warn",
            "Feature links to local implementation evidence."
            if implementation_references
            else "No local implementation references were found.",
        ),
        _check(
            "feature.test_references",
            "pass" if test_references else "warn",
            "Feature links to local test evidence."
            if test_references
            else "No local test references were found.",
        ),
        _check(
            "feature.documentation_references",
            "pass" if documentation_references else "warn",
            "Feature links to local documentation evidence."
            if documentation_references
            else "No local documentation references were found.",
        ),
    ]
    if changed_files:
        checks.append(
            _check(
                "feature.changed_references",
                "pass" if changed_references else "warn",
                "Changed paths intersect this feature evidence."
                if changed_references
                else "No changed paths intersect this feature evidence.",
            )
        )
    return tuple(checks)
