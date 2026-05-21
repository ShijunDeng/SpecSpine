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
    IMPACT_TYPE_CODE,
    IMPACT_TYPE_FEATURE,
    IMPACT_TYPE_TEST,
    ImpactAnalysis,
    ImpactItem,
)


def _compute_risk_score(
    impacted_features: tuple[ImpactItem, ...],
    impacted_tests: tuple[ImpactItem, ...],
    impacted_code: tuple[ImpactItem, ...],
) -> int:
    from .impact_models import SEVERITY_HIGH, SEVERITY_LOW, SEVERITY_MEDIUM
    score = 0

    high_count = sum(
        1 for item in impacted_features + impacted_tests + impacted_code
        if item.severity == SEVERITY_HIGH
    )
    medium_count = sum(
        1 for item in impacted_features + impacted_tests + impacted_code
        if item.severity == SEVERITY_MEDIUM
    )
    low_count = sum(
        1 for item in impacted_features + impacted_tests + impacted_code
        if item.severity == SEVERITY_LOW
    )

    score += high_count * 15
    score += medium_count * 8
    score += low_count * 3

    feature_count = len(impacted_features)
    test_count = len(impacted_tests)
    code_count = len(impacted_code)

    if feature_count > 3:
        score += 20
    elif feature_count > 1:
        score += 10

    if test_count > 5:
        score += 15
    elif test_count > 2:
        score += 8

    if code_count > 5:
        score += 10
    elif code_count > 2:
        score += 5

    return min(score, 100)


def _generate_mitigation_steps(analysis: ImpactAnalysis) -> list[str]:
    steps: list[str] = []

    if analysis.impacted_features:
        slugs = ", ".join(item.id for item in analysis.impacted_features[:5])
        steps.append(
            f"Review dependent features before merging changes: {slugs}"
        )
        steps.append(
            "Update dependent feature specs if API contracts or behaviors change"
        )

    if analysis.impacted_tests:
        test_paths = ", ".join(item.path for item in analysis.impacted_tests[:5])
        steps.append(
            f"Update impacted tests to reflect new behavior: {test_paths}"
        )
        steps.append(
            "Run full test suite after changes to catch regressions"
        )

    if analysis.impacted_code:
        code_paths = ", ".join(item.path for item in analysis.impacted_code[:5])
        steps.append(
            f"Review code changes in impacted modules: {code_paths}"
        )

    if analysis.risk_score >= 50:
        steps.append(
            "High risk score detected: consider breaking changes into smaller PRs"
        )

    if analysis.risk_score >= 75:
        steps.append(
            "Critical risk score: require additional peer review before merging"
        )

    steps.append(
        f"Run 'specspine impact analyze {analysis.feature_id} . --json' after changes to re-assess"
    )
    steps.append(
        "Run 'specspine validate . --fusion --features' before handoff or release"
    )

    return steps


def _generate_recommended_commands(slug: str) -> tuple[str, ...]:
    commands = [
        f"specspine impact analyze {slug} . --json",
        f"specspine consistency scan . --feature {slug} --json",
        f"specspine tests impact . --feature {slug} --json",
        f"specspine verify matrix {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        "specspine validate . --fusion --features",
    ]
    return tuple(commands)


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


__all__ = [
    "_compute_risk_score",
    "_generate_mitigation_steps",
    "_generate_recommended_commands",
    "analyze_feature_impact",
]
