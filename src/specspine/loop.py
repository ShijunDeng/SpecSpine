from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from .status import build_status


StatusBuilder = Callable[..., dict[str, Any]]


LOCAL_COMMAND_FLAGS = {
    "creates_remote": False,
    "executed": False,
    "requires_network": False,
    "requires_token": False,
    "safe_to_auto_run": False,
}


LIFECYCLE_COMMANDS: dict[str, tuple[str, ...]] = {
    "proposed": (
        'specspine feature new <slug> . --title "..." --why "..."',
        "specspine feature status <slug> . --set planned --enforce-transition --json",
    ),
    "planned": (
        "specspine feature handoff <slug> . --json",
        "specspine feature tasks <slug> . --json",
    ),
    "in-progress": (
        "specspine feature tasks <slug> . --json",
        "specspine feature trace <slug> . --json",
    ),
    "implemented": (
        "specspine feature tests <slug> . --json",
        "specspine feature ready <slug> . --json",
    ),
    "validated": (
        "specspine feature pr <slug> . --json",
        "specspine validate . --fusion --features",
    ),
    "archived": (
        "specspine status . --json --validate",
    ),
}


CONTEXT_COMMANDS: tuple[dict[str, object], ...] = (
    {
        "id": "workspace-status",
        "description": "Load local workspace, fusion, feature summary, and readiness context.",
        "command": (
            "specspine status . --json --validate "
            "--feature-summaries --readiness-summary"
        ),
    },
    {
        "id": "feature-handoff",
        "description": "Open the focused local implementation packet for one feature.",
        "command": "specspine feature handoff <slug> . --json",
    },
    {
        "id": "feature-tasks",
        "description": "Read the focused local execution checklist for one feature.",
        "command": "specspine feature tasks <slug> . --json",
    },
    {
        "id": "feature-ready",
        "description": "Evaluate the local per-feature readiness gate.",
        "command": "specspine feature ready <slug> . --json",
    },
    {
        "id": "coverage-debt",
        "description": "Inspect local acceptance-criteria coverage debt.",
        "command": "specspine coverage debt . --json --policy",
    },
)


VALIDATION_COMMANDS: tuple[dict[str, object], ...] = (
    {
        "id": "unit-tests",
        "description": "Run the local Python unit test suite.",
        "command": "PYTHONPATH=src python3 -m unittest discover -s tests",
    },
    {
        "id": "workspace-validation",
        "description": "Validate workspace, fusion, and native feature contracts.",
        "command": "PYTHONPATH=src python3 -m specspine validate . --fusion --features",
    },
    {
        "id": "status-validation",
        "description": "Export local status with validation and feature summaries.",
        "command": (
            "PYTHONPATH=src python3 -m specspine status . --json --validate "
            "--feature-summaries --readiness-summary"
        ),
    },
)


SUBAGENTS: tuple[dict[str, object], ...] = (
    {
        "id": "implementation-worker",
        "focus": "Implement one native feature from local spec, execution, and quality evidence.",
        "inputs": (
            "specspine feature handoff <slug> . --json",
            "specspine feature tasks <slug> . --json",
        ),
        "outputs": (
            "code changes",
            "updated native feature bundle evidence",
        ),
    },
    {
        "id": "validation-worker",
        "focus": "Run focused local tests and readiness checks without remote services.",
        "inputs": (
            "specspine feature tests <slug> . --json",
            "specspine feature ready <slug> . --json",
        ),
        "outputs": (
            "test results",
            "readiness evidence",
        ),
    },
    {
        "id": "review-worker",
        "focus": "Review traceability, blockers, release readiness, and documentation.",
        "inputs": (
            "specspine feature trace <slug> . --json",
            "specspine feature pr <slug> . --json",
        ),
        "outputs": (
            "review notes",
            "quality gate updates",
        ),
    },
)


SAFETY_NOTES: tuple[str, ...] = (
    "The loop packet is local and deterministic.",
    "The builder does not call GitHub APIs, read or write tokens, invoke subprocesses, probe adapters, or access the network.",
    "Recommended commands are plan data only; every command is marked executed=false.",
    "The only write performed by the CLI is an explicit --output text packet write.",
)


def _forbidden_adapter_probe() -> list[object]:
    raise RuntimeError("loop packet must not probe external adapters")


def _command_record(command: dict[str, object]) -> dict[str, object]:
    return {
        **LOCAL_COMMAND_FLAGS,
        "command": str(command["command"]),
        "description": str(command["description"]),
        "id": str(command["id"]),
    }


def _validation_command_record(command: dict[str, object]) -> dict[str, object]:
    return _command_record(command)


def _lifecycle_steps() -> list[dict[str, object]]:
    return [
        {
            "status": status,
            "commands": [
                {
                    **LOCAL_COMMAND_FLAGS,
                    "command": command,
                }
                for command in commands
            ],
        }
        for status, commands in LIFECYCLE_COMMANDS.items()
    ]


def _subagent_record(subagent: dict[str, object]) -> dict[str, object]:
    return {
        "focus": str(subagent["focus"]),
        "id": str(subagent["id"]),
        "inputs": list(subagent["inputs"]),
        "outputs": list(subagent["outputs"]),
        "safety": dict(LOCAL_COMMAND_FLAGS),
    }


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


def render_loop_packet_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def render_loop_packet_text(packet: dict[str, Any]) -> str:
    lines = [
        "# SpecSpine Agent Loop Packet",
        "",
        f"Root: {packet['root']}",
        f"Deadline: {packet['deadline'] or 'none'}",
        "",
        "## Summary",
    ]
    summary = packet["summary"]
    for key in (
        "features_total",
        "features_ready",
        "features_not_ready",
        "tasks_open_total",
        "gaps_total",
        "blocking_checks_total",
        "enabled_upstreams",
    ):
        lines.append(f"- {key}: {summary[key]}")

    lines.extend(["", "## Core Features"])
    core_features = packet["core_features"]
    if core_features:
        for feature in core_features:
            lines.append(
                "- "
                f"{feature['slug']} "
                f"status={feature['status']} "
                f"ready={'yes' if feature['ready'] else 'no'} "
                f"tasks_open={feature['tasks_summary'].get('open', 0)} "
                f"gaps={feature['gaps']} "
                f"blocking={feature['blocking_checks']}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Context Commands"])
    for command in packet["context_commands"]:
        lines.append(f"- {command['id']}: `{command['command']}`")

    lines.extend(["", "## Lifecycle Steps"])
    for step in packet["lifecycle_steps"]:
        lines.append(f"- {step['status']}")
        for command in step["commands"]:
            lines.append(f"  - `{command['command']}`")

    lines.extend(["", "## Subagents"])
    for subagent in packet["subagents"]:
        lines.append(f"- {subagent['id']}: {subagent['focus']}")

    lines.extend(["", "## Validation Commands"])
    for command in packet["validation_commands"]:
        lines.append(f"- {command['id']}: `{command['command']}`")

    lines.extend(["", "## Safety Notes"])
    for note in packet["safety_notes"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Upstreams"])
    upstreams = packet["upstreams"]
    if upstreams:
        for key in sorted(upstreams):
            upstream = upstreams[key]
            enabled = "enabled" if upstream.get("enabled") else "disabled"
            config = upstream.get("config", "")
            lines.append(f"- {key}: {enabled}, config={config}")
    else:
        lines.append("- none")

    lines.extend(["", "## Recommended Commands"])
    for command in packet["recommended_commands"]:
        lines.append(f"- `{command}`")

    return "\n".join(lines) + "\n"
