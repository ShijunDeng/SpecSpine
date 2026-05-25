from __future__ import annotations

from typing import Any

__all__ = [
    "_feature_summary_tasks_open",
]


def _feature_summary_tasks_open(summary: dict[str, Any]) -> int:
    tasks = summary.get("tasks_summary", {})
    if not isinstance(tasks, dict):
        return 0
    value = tasks.get("open", 0)
    return int(value) if isinstance(value, int) else 0
