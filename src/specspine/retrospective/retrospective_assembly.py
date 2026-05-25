from __future__ import annotations

from pathlib import Path

from ..features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    list_feature_bundles,
)

from .retrospective_commands import _workspace_commands
from .retrospective_constants import SAFETY_NOTES
from .retrospective_records import _feature_record
from .retrospective_summary import _empty_report, _summary, _themes

__all__ = [
    "_assemble_retrospective_report",
    "retrospective_report_exit_code",
]


def _assemble_retrospective_report(
    resolved_root: Path,
    *,
    feature_slug: str | None = None,
    limit: int | None = None,
) -> dict[str, object]:
    bundles = list_feature_bundles(resolved_root)
    slugs = [str(bundle["slug"]) for bundle in bundles]
    if feature_slug is not None:
        if feature_slug not in slugs:
            return _empty_report(
                resolved_root,
                feature_filter=feature_slug,
                missing_feature=feature_slug,
                limit=limit,
            )
        slugs = [feature_slug]

    features: list[dict[str, object]] = []
    for slug in slugs:
        try:
            features.append(_feature_record(resolved_root, slug))
        except (FeatureBundleNotFoundError, InvalidFeatureSlug):
            continue

    from .retrospective_recommendations import _build_recommendations

    return {
        "features": features,
        "feature_filter": feature_slug,
        "recommendations": _build_recommendations(features, limit=limit),
        "recommended_commands": _workspace_commands(feature_slug),
        "root": str(resolved_root),
        "safety_notes": list(SAFETY_NOTES),
        "summary": _summary(features, missing_feature=None),
        "themes": _themes(features),
    }


def retrospective_report_exit_code(report: dict[str, object]) -> int:
    summary = report.get("summary", {})
    if isinstance(summary, dict) and summary.get("missing_feature"):
        return 1
    return 0
