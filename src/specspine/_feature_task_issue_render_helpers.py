from __future__ import annotations

from .feature_bundle import (
    FeatureTask,
)

__all__ = [
    "_recommended_task_issue_commands",
    "_truncate_issue_title_text",
    "_feature_task_issue_title",
]


def _recommended_task_issue_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature tasks {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        "specspine validate . --fusion --features",
    )


def _truncate_issue_title_text(text: str, *, limit: int = 80) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _feature_task_issue_title(slug: str, task: FeatureTask) -> str:
    return f"[{slug}] {task.id}: {_truncate_issue_title_text(task.text)}"
