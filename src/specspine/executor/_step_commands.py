from __future__ import annotations

__all__ = [
    "_build_verification_commands",
]


def _build_verification_commands(slug: str) -> list[str]:
    return [
        f"specspine verify matrix {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature ready {slug} . --json --require-coverage",
        f"specspine consistency scan . --feature {slug} --json",
        "specspine validate . --fusion --features",
    ]
