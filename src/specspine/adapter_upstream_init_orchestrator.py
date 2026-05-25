from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .adapter_models import CommandRunner, UpstreamCommand, UpstreamCommandResult
from .adapter_upstream_probe import default_runner
from .adapter_upstream_init_probe_handler import _probe_command
from .adapter_upstream_init_executable_check import _check_executable

__all__ = [
    "run_upstream_initializers",
]


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
            results.append(_probe_command(command))
            continue

        not_found_result = _check_executable(command)
        if not_found_result is not None:
            results.append(not_found_result)
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
