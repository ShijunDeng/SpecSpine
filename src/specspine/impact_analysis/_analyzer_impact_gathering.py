from __future__ import annotations

from pathlib import Path
from typing import Any

from .impact_detection import (
    _find_affected_code,
    _find_affected_features,
    _find_affected_tests,
)
from .impact_analysis_risk_scoring import _compute_risk_score
from .impact_analysis_recommendations import (
    _generate_mitigation_steps,
    _generate_recommended_commands,
)
from .impact_models import (
    ImpactAnalysis,
)

__all__ = [
    "gather_impact_data",
    "build_impact_analysis",
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


def build_impact_analysis(
    slug: str,
    feature_items: tuple,
    test_items: tuple,
    code_items: tuple,
    total_affected: int,
    risk_score: int,
) -> ImpactAnalysis:
    preliminary = ImpactAnalysis(
        feature_id=slug,
        total_affected=total_affected,
        impacted_features=feature_items,
        impacted_tests=test_items,
        impacted_code=code_items,
        risk_score=risk_score,
        mitigation_steps=(),
        safety_notes=(
            "This command reads local workspace files only.",
            "It does not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
            "Impact predictions are static analysis only and do not prove actual runtime behavior.",
        ),
        recommended_commands=(),
    )

    mitigation_steps = _generate_mitigation_steps(preliminary)
    recommended_commands = _generate_recommended_commands(slug)

    return ImpactAnalysis(
        feature_id=slug,
        total_affected=total_affected,
        impacted_features=feature_items,
        impacted_tests=test_items,
        impacted_code=code_items,
        risk_score=risk_score,
        mitigation_steps=tuple(mitigation_steps),
        safety_notes=preliminary.safety_notes,
        recommended_commands=recommended_commands,
    )
