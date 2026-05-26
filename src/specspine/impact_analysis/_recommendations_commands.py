from __future__ import annotations

__all__ = [
    "_generate_recommended_commands",
]


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
