from __future__ import annotations


def _build_feature_commands(feature_slug: str | None) -> tuple[str, ...]:
    if feature_slug is not None:
        return (
            f"specspine review packet . --feature {feature_slug} --json",
            f"specspine feature handoff {feature_slug} . --json",
            f"specspine feature ready {feature_slug} . --json --require-coverage",
            f"specspine feature trace {feature_slug} . --json",
            f"specspine feature tests {feature_slug} . --json",
        )
    return ()


__all__ = [
    "_build_feature_commands",
]
