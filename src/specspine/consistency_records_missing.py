from __future__ import annotations

from pathlib import Path

from .consistency_models import (
    FeatureConsistency,
)
from .features import (
    FEATURE_FILE_PATHS,
)
from .consistency_checks import _check

__all__ = [
    "_missing_feature_record",
]


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
