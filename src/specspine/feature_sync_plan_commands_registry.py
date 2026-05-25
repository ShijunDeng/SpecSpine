from __future__ import annotations

__all__ = [
    "_recommended_sync_plan_commands",
]


def _recommended_sync_plan_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature sync-plan {slug} . --json",
        f"specspine feature issue {slug} . --json",
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature pr {slug} . --json",
        f"specspine feature ready {slug} . --json",
        "specspine adapters lifecycle . --json",
        "specspine validate . --fusion --features",
    )
