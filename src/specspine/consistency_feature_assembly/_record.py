from __future__ import annotations

from pathlib import Path

from ..consistency_models import FeatureConsistency
from ..features import (
    get_feature_status,
)

__all__ = [
    "_assemble_feature_record",
]


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
