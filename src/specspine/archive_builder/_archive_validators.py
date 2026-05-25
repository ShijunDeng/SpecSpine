from __future__ import annotations

from pathlib import Path

from specspine.features import (
    FeatureBundleNotFoundError,
    feature_bundle_paths,
    get_feature_status,
    validate_feature_slug,
)

from specspine.archive_helpers import (
    _default_archive_id,
    validate_archive_id,
)

__all__ = [
    "validate_archive_inputs",
]


def validate_archive_inputs(
    root: Path,
    slug: str,
    archive_id: str | None,
) -> tuple[str, Path, str]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    resolved_archive_id = validate_archive_id(archive_id or _default_archive_id(slug))

    status_report = get_feature_status(resolved_root, slug)
    has_native_files = any(file["exists"] for file in status_report.files.values())
    if not has_native_files:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(feature_bundle_paths(resolved_root, slug).values()),
        )

    return slug, resolved_root, resolved_archive_id
