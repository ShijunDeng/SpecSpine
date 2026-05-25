from __future__ import annotations

from pathlib import Path
from typing import Any

from .impact_detection import (
    _find_affected_code,
    _find_affected_features,
    _find_affected_tests,
)
from .impact_analysis_risk_scoring import _compute_risk_score

__all__ = [
    "gather_impact_data",
]


def gather_impact_data(
    slug: str,
    resolved_root: Path,
    proposed_changes: dict[str, Any] | None = None,
) -> tuple[tuple, tuple, tuple, int, int]:
    impacted_features = _find_affected_features(slug, resolved_root, proposed_changes)
    impacted_tests = _find_affected_tests(slug, resolved_root, proposed_changes)
    impacted_code = _find_affected_code(slug, resolved_root, proposed_changes)

    risk_score = _compute_risk_score(
        tuple(impacted_features),
        tuple(impacted_tests),
        tuple(impacted_code),
    )

    feature_items = tuple(impacted_features)
    test_items = tuple(impacted_tests)
    code_items = tuple(impacted_code)
    total_affected = len(feature_items) + len(test_items) + len(code_items)

    return feature_items, test_items, code_items, total_affected, risk_score
