from __future__ import annotations

from pathlib import Path

from .consistency_checks import _check
from .consistency_models import FeatureConsistency
from .consistency_feature_references import _gather_feature_references
from .features import (
    get_feature_status,
)

__all__ = [
    "_run_feature_checks",
    "_compute_feature_summary",
    "_assemble_feature_record",
]


def _run_feature_checks(refs: dict, changed_files: tuple[str, ...]) -> tuple:
    from .consistency_checks import _feature_checks
    return _feature_checks(
        source_files=refs["source_files"],
        missing_files=refs["missing_files"],
        implementation_references=refs["implementation_references"],
        test_references=refs["test_references"],
        documentation_references=refs["documentation_references"],
        changed_references=refs["changed_references"],
        changed_files=changed_files,
    )


def _compute_feature_summary(
    changed_references: list,
    checks: tuple,
    documentation_references: list,
    implementation_references: list,
    source_files: list,
    test_references: list,
) -> dict:
    return {
        "changed_references": len(changed_references),
        "checks_fail": sum(1 for check in checks if check.status == "fail"),
        "checks_pass": sum(1 for check in checks if check.status == "pass"),
        "checks_warn": sum(1 for check in checks if check.status == "warn"),
        "documentation_references": len(documentation_references),
        "implementation_references": len(implementation_references),
        "source_files": len(source_files),
        "test_references": len(test_references),
    }


def _assemble_feature_record(
    root: Path,
    slug: str,
    *,
    changed_files: tuple[str, ...],
    refs: dict,
    checks: tuple,
    summary: dict,
) -> FeatureConsistency:
    status_report = get_feature_status(root, slug)
    return FeatureConsistency(
        feature_id=slug,
        status=status_report.status,
        source_files=refs["source_files"],
        missing_files=refs["missing_files"],
        implementation_references=refs["implementation_references"],
        test_references=refs["test_references"],
        documentation_references=refs["documentation_references"],
        changed_references=refs["changed_references"],
        consistency_checks=checks,
        summary=summary,
    )
