from __future__ import annotations

from pathlib import Path


def _gather_quality_data(
    resolved_root: Path,
    slug: str,
    relative_paths: dict,
    require_coverage: bool,
) -> tuple:
    from ...feature_bundle import (
        FeatureTraceChecklistItem,
        FeatureTestCoverageLink,
        feature_bundle_paths,
        parse_release_readiness,
        parse_test_coverage,
    )
    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    release_readiness: tuple[FeatureTraceChecklistItem, ...] = ()
    test_coverage: tuple[FeatureTestCoverageLink, ...] = ()
    if quality_path.exists():
        quality_content = quality_path.read_text(encoding="utf-8")
        release_readiness = parse_release_readiness(
            quality_content,
            source_file=relative_paths["quality"],
        )
        if require_coverage:
            test_coverage = parse_test_coverage(
                quality_content,
                source_file=relative_paths["quality"],
                root=resolved_root,
            )
    return release_readiness, test_coverage


__all__ = [
    "_gather_quality_data",
]
