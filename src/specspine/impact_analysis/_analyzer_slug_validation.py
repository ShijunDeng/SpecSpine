from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    validate_feature_slug,
)

__all__ = [
    "resolve_feature_spec",
    "validate_and_resolve_slug",
]


def validate_and_resolve_slug(slug: str) -> str:
    return validate_feature_slug(slug)


def resolve_feature_spec(
    root: Path,
    slug: str,
) -> tuple[Path, Path]:
    resolved_root = root.expanduser().resolve()
    spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
    if not spec_path.exists():
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(
                resolved_root / FEATURE_FILE_PATHS[kind].format(slug=slug)
                for kind in FEATURE_FILE_PATHS
            ),
        )
    return resolved_root, spec_path
