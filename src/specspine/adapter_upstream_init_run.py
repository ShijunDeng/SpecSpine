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
    probe_adapter,
)


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
    "run_upstream_initializers",
]
