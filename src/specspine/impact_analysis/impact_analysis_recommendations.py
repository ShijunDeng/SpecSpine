from __future__ import annotations

from .impact_models import ImpactAnalysis

__all__ = [
    "_generate_mitigation_steps",
    "_generate_recommended_commands",
]


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
