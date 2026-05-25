from __future__ import annotations

from typing import Any

from ..status import build_status
from .constants import CONTEXT_COMMANDS, VALIDATION_COMMANDS, SAFETY_NOTES, SUBAGENTS
from .helpers import (
    _command_record,
    _forbidden_adapter_probe,
    _lifecycle_steps,
    _subagent_record,
    _validation_command_record,
)
from .builders_packet_features import _core_features
from .builders_packet_summary import _summary
from .builders_packet_commands import _recommended_commands
from .builders_types import StatusBuilder

__all__ = [
    "StatusBuilder",
    "_core_features",
    "_summary",
    "_recommended_commands",
    "build_loop_packet",
]


def build_loop_packet(
    path,
    *,
    deadline: str | None = None,
    status_builder: StatusBuilder = build_status,
) -> dict[str, Any]:
    from pathlib import Path
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
