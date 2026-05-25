from __future__ import annotations

from pathlib import Path

from ..features import validate_feature_slug

__all__ = [
    "_validate_retrospective_input",
]


def _validate_retrospective_input(
    root: Path,
    *,
    feature_slug: str | None = None,
    limit: int | None = None,
) -> tuple[Path, str | None]:
    if limit is not None and limit < 0:
        raise ValueError("limit must be a nonnegative integer")

    resolved_root = root.expanduser().resolve()
    if not resolved_root.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved_root}")
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {resolved_root}")
    if feature_slug is not None:
        feature_slug = validate_feature_slug(feature_slug)

    return resolved_root, feature_slug
