from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

from .adapter_models import (
    ADAPTER_SPECS,
    CommandRunner,
    UpstreamCommand,
    UpstreamCommandResult,
)
from .adapter_upstream_probe import (
    default_runner,
    get_agent_profile,
    probe_adapter,
)


def build_upstream_init_commands(
    *,
    agent: str,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
    force: bool = False,
) -> list[UpstreamCommand]:
    profile = get_agent_profile(agent)
    commands: list[UpstreamCommand] = []

    if include_openspec:
        args = ["openspec", "init", ".", "--tools", profile.openspec_tool]
        if force:
            args.append("--force")
        commands.append(
            UpstreamCommand(
                key="openspec",
                description="Initialize OpenSpec using its own CLI.",
                args=tuple(args),
            )
        )

    if include_speckit:
        commands.append(
            UpstreamCommand(
                key="speckit",
                description="Initialize Spec Kit using its own Specify CLI.",
                args=("specify", "init", ".", "--integration", profile.speckit_integration),
            )
        )

    if include_superpowers:
        commands.append(
            UpstreamCommand(
                key="superpowers",
                description="Verify that the Superpowers agent plugin/extension is installed.",
                args=(),
            )
        )

    return commands


def run_upstream_initializers(
    root: Path,
    commands: Iterable[UpstreamCommand],
    *,
    runner: CommandRunner = default_runner,
) -> list[UpstreamCommandResult]:
    results: list[UpstreamCommandResult] = []
    root = root.expanduser().resolve()

    for command in commands:
        if not command.args:
            status = probe_adapter(command.key)
            results.append(
                UpstreamCommandResult(
                    key=command.key,
                    command=command.description,
                    returncode=0 if status.available else 1,
                    stdout=status.detail,
                    stderr="" if status.available else status.install_hint,
                )
            )
            continue

        executable = command.args[0]
        if shutil.which(executable) is None:
            spec = ADAPTER_SPECS[command.key]
            results.append(
                UpstreamCommandResult(
                    key=command.key,
                    command=command.display(),
                    returncode=127,
                    stdout="",
                    stderr=f"{executable!r} is not installed. {spec.install_hint}",
                )
            )
            continue

        result = runner(command.args, root)
        results.append(
            UpstreamCommandResult(
                key=command.key,
                command=command.display(),
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        )

    return results


__all__ = [
    "build_upstream_init_commands",
    "run_upstream_initializers",
]
