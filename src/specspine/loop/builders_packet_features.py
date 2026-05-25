from __future__ import annotations

from typing import Any

__all__ = [
    "_core_features",
]


def _core_features(status: dict[str, Any]) -> list[dict[str, object]]:
    summaries = status.get("feature_summaries", [])
    if not isinstance(summaries, list):
        return []

    records: list[dict[str, object]] = []
    for summary in summaries:
        if not isinstance(summary, dict):
            continue
        tasks = summary.get("tasks_summary", {})
        ready = summary.get("ready_summary", {})
        records.append(
            {
                "feature_id": str(summary.get("feature_id") or summary.get("slug") or ""),
                "slug": str(summary.get("slug") or summary.get("feature_id") or ""),
                "status": str(summary.get("status") or "unknown"),
                "ready": bool(summary.get("ready", False)),
                "priority": str(summary.get("priority") or "unknown"),
                "owner": str(summary.get("owner") or "unassigned"),
                "tasks_summary": dict(tasks) if isinstance(tasks, dict) else {},
                "ready_summary": dict(ready) if isinstance(ready, dict) else {},
                "gaps": int(summary.get("gaps", 0)),
                "blocking_checks": int(summary.get("blocking_checks", 0)),
                "next_actions": list(summary.get("next_actions", [])),
                "recommended_commands": list(summary.get("recommended_commands", [])),
            }
        )
    return sorted(records, key=lambda record: str(record["slug"]))
