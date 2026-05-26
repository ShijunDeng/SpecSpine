from __future__ import annotations

from typing import Any

from ._debt_record_paths import _resolve_feature_paths
from ._debt_coverage_analysis import _analyze_feature_coverage_gaps


def _gather_debt_analysis(
    root,
    slug: str,
) -> dict[str, Any]:
    paths, relative_paths = _resolve_feature_paths(slug, root)

    analysis = _analyze_feature_coverage_gaps(
        root,
        slug,
        paths["quality"],
        source_file=relative_paths["quality"],
    )

    return {
        "paths": paths,
        "relative_paths": relative_paths,
        "trace_report": analysis["trace_report"],
        "covered_ids": analysis["covered_ids"],
        "missing_ids": analysis["missing_ids"],
        "open_link_ids": analysis["open_link_ids"],
        "missing_target_link_ids": analysis["missing_target_link_ids"],
        "unknown_link_ids": analysis["unknown_link_ids"],
    }


__all__ = [
    "_gather_debt_analysis",
]
