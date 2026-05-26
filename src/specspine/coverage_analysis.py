from __future__ import annotations

from pathlib import Path

from .features import (
    feature_bundle_paths,
    parse_test_coverage,
)

__all__ = [
    "_existing_coverage_links",
]


def _existing_coverage_links(root: Path, slug: str) -> set[str]:
    quality_path = feature_bundle_paths(root, slug)["quality"]
    covered: set[str] = set()
    if not quality_path.exists():
        return covered
    coverage = parse_test_coverage(
        quality_path.read_text(encoding="utf-8"),
        source_file=str(quality_path),
        root=root,
    )
    for link in coverage:
        if link.done and link.target_exists:
            covered.add(link.acceptance_criterion_id)
    return covered
