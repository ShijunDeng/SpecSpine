from __future__ import annotations

from pathlib import Path

from .consistency_checks import _check, _feature_checks
from .consistency_models import (
    FeatureConsistency,
    DOCUMENTATION_GLOBS,
    IMPLEMENTATION_GLOBS,
    TEST_GLOBS,
)
from .consistency_references import (
    _changed_references,
    _coverage_references,
    _explicit_paths_from_feature_files,
    _feature_missing_files,
    _feature_source_files,
    _references_for_area,
)
from .consistency_utils import _dedupe_references
from .features import (
    FEATURE_FILE_PATHS,
    build_feature_tests_report,
    get_feature_status,
)

__all__ = [
    "_build_feature_record",
    "_missing_feature_record",
]


def _build_feature_record(
    root: Path,
    slug: str,
    *,
    changed_files: tuple[str, ...],
) -> FeatureConsistency:
    status_report = get_feature_status(root, slug)
    source_files = _feature_source_files(root, slug)
    missing_files = _feature_missing_files(root, slug)
    explicit_paths = _explicit_paths_from_feature_files(root, source_files)
    implementation_references = _references_for_area(
        root,
        slug=slug,
        explicit_paths=explicit_paths,
        globs=IMPLEMENTATION_GLOBS,
        area="implementation",
    )
    test_references = _references_for_area(
        root,
        slug=slug,
        explicit_paths=explicit_paths,
        globs=TEST_GLOBS,
        area="test",
    )
    test_references = _dedupe_references(
        list(test_references)
        + list(_coverage_references(build_feature_tests_report(root, slug)))
    )
    documentation_references = _references_for_area(
        root,
        slug=slug,
        explicit_paths=explicit_paths,
        globs=DOCUMENTATION_GLOBS,
        area="documentation",
    )
    changed_reference_list = _changed_references(
        root=root,
        slug=slug,
        changed_files=changed_files,
        source_files=source_files,
        implementation_references=implementation_references,
        test_references=test_references,
        documentation_references=documentation_references,
    )
    checks = _feature_checks(
        source_files=source_files,
        missing_files=missing_files,
        implementation_references=implementation_references,
        test_references=test_references,
        documentation_references=documentation_references,
        changed_references=changed_reference_list,
        changed_files=changed_files,
    )
    summary = {
        "changed_references": len(changed_reference_list),
        "checks_fail": sum(1 for check in checks if check.status == "fail"),
        "checks_pass": sum(1 for check in checks if check.status == "pass"),
        "checks_warn": sum(1 for check in checks if check.status == "warn"),
        "documentation_references": len(documentation_references),
        "implementation_references": len(implementation_references),
        "source_files": len(source_files),
        "test_references": len(test_references),
    }
    return FeatureConsistency(
        feature_id=slug,
        status=status_report.status,
        source_files=source_files,
        missing_files=missing_files,
        implementation_references=implementation_references,
        test_references=test_references,
        documentation_references=documentation_references,
        changed_references=changed_reference_list,
        consistency_checks=checks,
        summary=summary,
    )


def _missing_feature_record(root: Path, slug: str) -> FeatureConsistency:
    missing_files = tuple(
        relative_path.format(slug=slug) for relative_path in FEATURE_FILE_PATHS.values()
    )
    checks = (
        _check(
            "feature.bundle_files",
            "fail",
            f"No native feature files found for '{slug}'.",
        ),
    )
    return FeatureConsistency(
        feature_id=slug,
        status=None,
        source_files=(),
        missing_files=missing_files,
        implementation_references=(),
        test_references=(),
        documentation_references=(),
        changed_references=(),
        consistency_checks=checks,
        summary={
            "changed_references": 0,
            "checks_fail": 1,
            "checks_pass": 0,
            "checks_warn": 0,
            "documentation_references": 0,
            "implementation_references": 0,
            "source_files": 0,
            "test_references": 0,
        },
    )
