from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    validate_feature_slug,
)

from .impact_detection import (
    _find_affected_code,
    _find_affected_features,
    _find_affected_tests,
)
from .impact_models import (
    ImpactAnalysis,
)
from .impact_analysis_risk_scoring import _compute_risk_score
from .impact_analysis_recommendations import (
    _generate_mitigation_steps,
    _generate_recommended_commands,
)

__all__ = [
    "analyze_feature_impact",
]


def analyze_feature_impact(
    root: Path,
    slug: str,
    proposed_changes: dict[str, Any] | None = None,
) -> ImpactAnalysis:
    resolved_root = root.expanduser().resolve()
    slug = validate_feature_slug(slug)

    spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
    if not spec_path.exists():
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(
                resolved_root / FEATURE_FILE_PATHS[kind].format(slug=slug)
                for kind in FEATURE_FILE_PATHS
            ),
        )

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
