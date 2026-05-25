from __future__ import annotations

from pathlib import Path
from typing import Any

from ._analyzer_slug_validation import (
    resolve_feature_spec,
    validate_and_resolve_slug,
)
from ._analyzer_impact_gathering import (
    gather_impact_data,
    build_impact_analysis,
)
from .impact_models import ImpactAnalysis

__all__ = [
    "analyze_feature_impact",
]


def analyze_feature_impact(
    root: Path,
    slug: str,
    proposed_changes: dict[str, Any] | None = None,
) -> ImpactAnalysis:
    slug = validate_and_resolve_slug(slug)
    resolved_root, _spec_path = resolve_feature_spec(root, slug)

    feature_items, test_items, code_items, total_affected, risk_score = gather_impact_data(
        slug, resolved_root, proposed_changes
    )

    return build_impact_analysis(
        slug, feature_items, test_items, code_items, total_affected, risk_score
    )
