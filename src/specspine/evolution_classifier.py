from __future__ import annotations

from pathlib import Path

from .features import validate_feature_slug
from .evolution_git import DiffResult
from .evolution_classification_models import (
    ClassifiedChange,
    ClassificationResult,
)
from .evolution_content_loader import load_feature_contents
from ._evolution_file_classifier import _classify_file_changes
from ._evolution_metadata_comparator import _compare_metadata

__all__ = [
    "classify_changes",
]


def classify_changes(
    diff_result: DiffResult,
    slug: str,
    root: Path,
) -> ClassificationResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    base_contents, current_contents = load_feature_contents(resolved_root, slug)

    changes: list[ClassifiedChange] = []
    change_counter = 0

    file_changes, change_counter = _classify_file_changes(
        base_contents, current_contents, slug, change_counter, diff_result
    )
    changes.extend(file_changes)

    metadata_changes, change_counter = _compare_metadata(
        base_contents.get("spec"),
        current_contents.get("spec"),
        slug,
        change_counter,
    )
    changes.extend(metadata_changes)

    return ClassificationResult(slug=slug, changes=changes)
