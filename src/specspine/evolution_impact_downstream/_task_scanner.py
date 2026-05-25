from __future__ import annotations

from pathlib import Path

from ..features import (
    InvalidFeatureSlug,
    build_feature_trace_report,
    list_feature_bundles,
)

__all__ = [
    "_scan_task_downstream",
]


def _scan_task_downstream(
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
            trace = build_feature_trace_report(root, feature_slug)
            for ac in trace.acceptance_criteria:
                if slug.lower() in ac.text.lower():
                    references.append({
                        "feature_id": feature_slug,
                        "item_id": ac.id,
                        "text": ac.text,
                    })
        except (InvalidFeatureSlug, OSError):
            continue
    return references
