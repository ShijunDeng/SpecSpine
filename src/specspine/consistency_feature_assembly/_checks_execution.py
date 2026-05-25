from __future__ import annotations

__all__ = [
    "_run_feature_checks",
]


def _run_feature_checks(refs: dict, changed_files: tuple[str, ...]) -> tuple:
    from ..consistency_checks import _feature_checks
    return _feature_checks(
        source_files=refs["source_files"],
        missing_files=refs["missing_files"],
        implementation_references=refs["implementation_references"],
        test_references=refs["test_references"],
        documentation_references=refs["documentation_references"],
        changed_references=refs["changed_references"],
        changed_files=changed_files,
    )
