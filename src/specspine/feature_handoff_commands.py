from __future__ import annotations

__all__ = [
    "_recommended_handoff_commands",
]


def _recommended_handoff_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature handoff {slug} . --json",
        f"specspine feature tasks {slug} . --json",
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature ready {slug} . --json",
        f"specspine feature pr {slug} . --json",
        "specspine validate . --fusion --features",
    )
