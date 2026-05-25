from __future__ import annotations

import shlex
from pathlib import Path

from ..feature_bundle import (
    FeatureSyncPlan,
    _path_as_posix,
)

__all__ = [
    "_argv_with_local_body_file",
    "_render_sync_plan_commands_sh",
]


def _argv_with_local_body_file(
    argv: tuple[str, ...],
    body_file: str,
) -> tuple[str, ...]:
    updated = list(argv)
    for index, arg in enumerate(updated[:-1]):
        if arg == "--body-file":
            updated[index + 1] = body_file
            return tuple(updated)
    return (*argv, "--body-file", body_file)


def _render_sync_plan_commands_sh(
    plan: FeatureSyncPlan,
    artifact_paths: dict[str, Path],
) -> str:
    lines = [
        "# SpecSpine GitHub sync plan artifacts",
        "# review-only / do not run blindly",
        "# SpecSpine did not execute gh, read tokens, call GitHub APIs, or use the network.",
        "# Review manifest.json and the body files before manually running any command.",
        "",
    ]

    for command in plan.commands:
        body_file = _path_as_posix(artifact_paths[command.id])
        argv = _argv_with_local_body_file(command.argv, body_file)
        lines.extend(
            [
                f"# {command.id}: {command.description}",
                shlex.join(argv),
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"
