from __future__ import annotations

import shutil

from .adapter_models import ADAPTER_SPECS, UpstreamCommandResult

__all__ = [
    "_check_executable",
]


def _check_executable(command) -> UpstreamCommandResult | None:
    executable = command.args[0]
    if shutil.which(executable) is None:
        spec = ADAPTER_SPECS[command.key]
        return UpstreamCommandResult(
            key=command.key,
            command=command.display(),
            returncode=127,
            stdout="",
            stderr=f"{executable!r} is not installed. {spec.install_hint}",
        )
    return None
