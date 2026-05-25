from __future__ import annotations

from pathlib import Path

from ..feature_bundle_models import FeatureStatusReport
from ..feature_bundle_validation import validate_feature_slug
from ._status_aggregator import build_status_report
from ._status_file_reader import read_feature_files

__all__ = [
    "get_feature_status",
]


def get_feature_status(root: Path, slug: str) -> FeatureStatusReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    files, missing_files, statuses, status_missing = read_feature_files(
        resolved_root, slug
    )
    return build_status_report(slug, files, missing_files, statuses, status_missing)
