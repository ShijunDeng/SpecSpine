from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureTestCoverageLink,
    _relative_feature_paths,
    feature_bundle_paths,
    parse_test_coverage,
)
from .feature_handoff import FeatureHandoffReport

__all__ = [
    "extract_source_files",
    "parse_feature_test_coverage",
]


def extract_source_files(handoff: FeatureHandoffReport) -> tuple[str, ...]:
    return tuple(
        source["path"]
        for source in handoff.sources.values()
        if bool(source["exists"])
    )


def parse_feature_test_coverage(
    resolved_root: Path,
    slug: str,
) -> tuple[FeatureTestCoverageLink, ...]:
    test_coverage: tuple[FeatureTestCoverageLink, ...] = ()
    relative_paths = _relative_feature_paths(slug)
    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    if quality_path.exists():
        test_coverage = parse_test_coverage(
            quality_path.read_text(encoding="utf-8"),
            source_file=relative_paths["quality"],
            root=resolved_root,
        )
    return test_coverage
