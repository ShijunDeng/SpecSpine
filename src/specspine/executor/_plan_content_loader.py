from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    get_feature_status,
    validate_feature_slug,
)

from .executor_steps import _read_feature_contents


def load_plan_context(
    slug: str,
    root: Path,
) -> dict[str, Any]:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    relative_paths = {
        kind: pattern.format(slug=slug)
        for kind, pattern in FEATURE_FILE_PATHS.items()
    }

    status_report = get_feature_status(resolved_root, feature_id)
    feature_status = status_report.status or "unknown"

    contents = _read_feature_contents(resolved_root, feature_id)
    if not contents:
        missing = [relative_paths[k] for k in FEATURE_FILE_PATHS]
        raise FeatureBundleNotFoundError(
            slug=feature_id,
            root=resolved_root,
            missing_paths=tuple(resolved_root / p for p in missing),
        )

    return {
        "feature_id": feature_id,
        "resolved_root": resolved_root,
        "relative_paths": relative_paths,
        "feature_status": feature_status,
        "contents": contents,
        "slug": slug,
    }


__all__ = [
    "load_plan_context",
]
