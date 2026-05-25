from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureTraceChecklistItem,
    feature_bundle_paths,
    parse_release_readiness,
)
from .feature_bundle_io_paths import _relative_feature_paths


def _parse_release_readiness_from_file(
    resolved_root: Path,
    slug: str,
) -> tuple[FeatureTraceChecklistItem, ...]:
    relative_paths = _relative_feature_paths(slug)
    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    if quality_path.exists():
        return parse_release_readiness(
            quality_path.read_text(encoding="utf-8"),
            source_file=relative_paths["quality"],
        )
    return ()


__all__ = [
    "_parse_release_readiness_from_file",
]
