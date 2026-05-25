from __future__ import annotations

from .impact_analysis_recommendations import (
    _generate_mitigation_steps,
    _generate_recommended_commands,
)
from .impact_models import (
    ImpactAnalysis,
)

__all__ = [
    "build_impact_analysis",
]


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
