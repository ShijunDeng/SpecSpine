from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from ..status import build_status
from .constants import CONTEXT_COMMANDS, VALIDATION_COMMANDS, SAFETY_NOTES, SUBAGENTS
from .helpers import (
    _command_record,
    _forbidden_adapter_probe,
    _lifecycle_steps,
    _subagent_record,
    _validation_command_record,
)

__all__ = [
    "StatusBuilder",
    "build_loop_packet",
]

StatusBuilder = Callable[..., dict[str, Any]]


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


def _summary(status: dict[str, Any], core_features: list[dict[str, object]]) -> dict[str, int]:
    readiness = status.get("readiness_summary", {})
    if not isinstance(readiness, dict):
        readiness = {}
    upstreams = status.get("upstreams", {})
    if not isinstance(upstreams, dict):
        upstreams = {}

    return {
        "features_total": len(core_features),
        "features_ready": int(readiness.get("ready", 0)),
        "features_not_ready": int(readiness.get("not_ready", 0)),
        "tasks_open_total": sum(
            int(feature.get("tasks_summary", {}).get("open", 0))
            for feature in core_features
            if isinstance(feature.get("tasks_summary", {}), dict)
        ),
        "gaps_total": int(readiness.get("gaps_total", 0)),
        "blocking_checks_total": int(readiness.get("blocking_checks_total", 0)),
        "enabled_upstreams": sum(
            1
            for upstream in upstreams.values()
            if isinstance(upstream, dict) and bool(upstream.get("enabled", False))
        ),
    }


def _recommended_commands(
    status: dict[str, Any],
    validation_commands: list[dict[str, object]],
) -> list[str]:
    commands: list[str] = []
    for recommendation in status.get("recommendations", []):
        if isinstance(recommendation, str) and recommendation not in commands:
            commands.append(recommendation)
    readiness = status.get("readiness_summary", {})
    if isinstance(readiness, dict):
        for command in readiness.get("recommended_commands", []):
            if isinstance(command, str) and command not in commands:
                commands.append(command)
    for command in validation_commands:
        value = str(command["command"])
        if value not in commands:
            commands.append(value)
    if "specspine loop packet . --json" not in commands:
        commands.append("specspine loop packet . --json")
    return commands


def build_loop_packet(
    path: Path,
    *,
    deadline: str | None = None,
    status_builder: StatusBuilder = build_status,
) -> dict[str, Any]:
    root = path.expanduser().resolve()
    status = status_builder(
        root,
        include_adapters=False,
        include_feature_summaries=True,
        include_readiness_summary=True,
        feature_summary_sort="slug",
        adapter_probe=_forbidden_adapter_probe,
    )
    core_features = _core_features(status)
    context_commands = [_command_record(command) for command in CONTEXT_COMMANDS]
    validation_commands = [
        _validation_command_record(command) for command in VALIDATION_COMMANDS
    ]

    return {
        "root": str(root),
        "deadline": deadline,
        "core_features": core_features,
        "summary": _summary(status, core_features),
        "context_commands": context_commands,
        "lifecycle_steps": _lifecycle_steps(),
        "subagents": [_subagent_record(subagent) for subagent in SUBAGENTS],
        "validation_commands": validation_commands,
        "safety_notes": list(SAFETY_NOTES),
        "upstreams": status.get("upstreams", {}),
        "recommended_commands": _recommended_commands(status, validation_commands),
    }
