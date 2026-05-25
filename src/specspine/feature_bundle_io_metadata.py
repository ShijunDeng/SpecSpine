from __future__ import annotations

from pathlib import Path

from .feature_bundle_models import (
    FeatureMetadata,
)
from .feature_bundle_io_paths import (
    feature_bundle_paths,
)
from .feature_bundle_render import _extract_scalar
from .feature_bundle_validation import (
    normalize_feature_assignment,
    normalize_feature_effort,
    normalize_feature_owner,
    normalize_feature_priority,
    validate_feature_slug,
)

__all__ = [
    "read_feature_metadata",
]


def read_feature_metadata(root: Path, slug: str) -> FeatureMetadata:
    slug = validate_feature_slug(slug)
    spec_path = feature_bundle_paths(root, slug)["spec"]
    if not spec_path.exists():
        return FeatureMetadata(
            priority="unknown",
            owner="unassigned",
            milestone="unassigned",
            target_release="unassigned",
            project="unassigned",
            effort="unknown",
        )

    content = spec_path.read_text(encoding="utf-8")
    return FeatureMetadata(
        priority=normalize_feature_priority(_extract_scalar(content, "Priority")),
        owner=normalize_feature_owner(_extract_scalar(content, "Owner")),
        milestone=normalize_feature_assignment(_extract_scalar(content, "Milestone")),
        target_release=normalize_feature_assignment(
            _extract_scalar(content, "Target Release")
        ),
        project=normalize_feature_assignment(_extract_scalar(content, "Project")),
        effort=normalize_feature_effort(_extract_scalar(content, "Effort")),
    )
