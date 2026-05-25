from __future__ import annotations

from pathlib import Path

from .consistency_models import FeatureConsistency
from .consistency_feature_references import _gather_feature_references
from .consistency_feature_assembly import (
    _run_feature_checks,
    _compute_feature_summary,
    _assemble_feature_record,
)

__all__ = [
    "_build_feature_record",
]


def _build_feature_record(
    root: Path,
    slug: str,
    *,
    changed_files: tuple[str, ...],
) -> FeatureConsistency:
    refs = _gather_feature_references(root, slug, changed_files=changed_files)
    checks = _run_feature_checks(refs, changed_files)
    summary = _compute_feature_summary(
        changed_references=refs["changed_references"],
        checks=checks,
        documentation_references=refs["documentation_references"],
        implementation_references=refs["implementation_references"],
        source_files=refs["source_files"],
        test_references=refs["test_references"],
    )
    return _assemble_feature_record(
        root,
        slug,
        changed_files=changed_files,
        refs=refs,
        checks=checks,
        summary=summary,
    )
