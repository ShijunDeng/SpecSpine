from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    validate_feature_slug,
)

from .executor_models import GradingRubric
from .executor_steps import (
    _read_feature_contents,
)
from .executor_rubric import _build_grading_rubric_internal

__all__ = [
    "build_grading_rubric",
]


def build_grading_rubric(slug: str, root: Path) -> dict[str, Any]:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    relative_paths = {
        kind: pattern.format(slug=slug)
        for kind, pattern in FEATURE_FILE_PATHS.items()
    }

    contents = _read_feature_contents(resolved_root, feature_id)
    if not contents:
        missing = [relative_paths[k] for k in FEATURE_FILE_PATHS]
        raise FeatureBundleNotFoundError(
            slug=feature_id,
            root=resolved_root,
            missing_paths=tuple(resolved_root / p for p in missing),
        )

    rubric_items = _build_grading_rubric_internal(contents, slug, resolved_root, relative_paths)

    rubric = GradingRubric(
        feature_id=feature_id,
        rubric_items=rubric_items,
    )

    return rubric.as_dict()
