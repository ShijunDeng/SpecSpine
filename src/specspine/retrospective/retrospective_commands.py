from __future__ import annotations

__all__ = [
    "_recommended_feature_commands",
    "_workspace_commands",
]


def _recommended_feature_commands(slug: str) -> list[str]:
    return [
        f"specspine feature ready {slug} . --json --require-coverage",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine verify matrix {slug} . --json",
        f"specspine review packet . --feature {slug} --json",
    ]


def _workspace_commands(feature_filter: str | None) -> list[str]:
    commands = ["specspine retrospective report . --json"]
    if feature_filter:
        commands.append(
            f"specspine retrospective report . --feature {feature_filter} --json"
        )
    commands.extend(
        [
            "specspine status . --json --validate --feature-summaries",
            "specspine coverage debt . --json",
            "specspine validate . --fusion --features",
        ]
    )
    return commands
