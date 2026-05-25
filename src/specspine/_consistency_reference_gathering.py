from __future__ import annotations

from pathlib import Path

from .consistency_models import (
    DOCUMENTATION_GLOBS,
    IMPLEMENTATION_GLOBS,
    TEST_GLOBS,
)
from .consistency_references import (
    _changed_references,
    _coverage_references,
    _references_for_area,
)
from .consistency_utils import _dedupe_references
from .features import (
    build_feature_tests_report,
)

__all__ = [
    "_gather_all_references",
]


def _gather_all_references(
    root: Path,
    slug: str,
    *,
    source_files: list[str],
    explicit_paths: list[str],
    changed_files: tuple[str, ...],
) -> dict[str, list[str]]:
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
    return {
        "implementation_references": implementation_references,
        "test_references": test_references,
        "documentation_references": documentation_references,
        "changed_references": changed_reference_list,
    }
