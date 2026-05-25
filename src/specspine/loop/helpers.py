from __future__ import annotations

from typing import Any

from .constants import LOCAL_COMMAND_FLAGS, LIFECYCLE_COMMANDS, SUBAGENTS

__all__ = [
    "_forbidden_adapter_probe",
    "_command_record",
    "_validation_command_record",
    "_lifecycle_steps",
    "_subagent_record",
]


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
