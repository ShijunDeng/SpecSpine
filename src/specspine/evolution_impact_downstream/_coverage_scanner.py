from __future__ import annotations

from pathlib import Path

from ..features import (
    InvalidFeatureSlug,
    build_feature_tests_report,
    list_feature_bundles,
)

__all__ = [
    "_scan_coverage_downstream",
]


def _scan_coverage_downstream(
    slug: str,
    root: Path,
    all_features: list[dict],
) -> list[dict[str, str]]:
    references: list[dict[str, str]] = []
    for feature in all_features:
        feature_slug = feature["slug"]
        if feature_slug == slug:
            continue
        try:
            tests_report = build_feature_tests_report(root, feature_slug)
            for coverage_link in tests_report.test_coverage:
                if slug.lower() in coverage_link.text.lower():
                    references.append({
                        "feature_id": feature_slug,
                        "coverage_id": coverage_link.id,
                        "text": coverage_link.text,
                    })
        except (InvalidFeatureSlug, OSError):
            continue
    return references
