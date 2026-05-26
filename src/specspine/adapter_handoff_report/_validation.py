from __future__ import annotations

from pathlib import Path

from specspine.features import (
    FeatureBundleNotFoundError,
    build_feature_handoff_report,
    feature_bundle_paths,
)

__all__ = [
    "validate_feature_bundle",
]


def validate_feature_bundle(
    root: Path,
    slug: str,
):
    resolved_root = root.expanduser().resolve()
    feature_report = build_feature_handoff_report(resolved_root, slug)
    if not feature_report.has_native_files:
        missing_paths = tuple(feature_bundle_paths(resolved_root, slug).values())
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=missing_paths,
        )
    return feature_report, resolved_root
