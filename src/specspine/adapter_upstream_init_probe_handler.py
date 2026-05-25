from __future__ import annotations

from .adapter_models import UpstreamCommandResult
from .adapter_upstream_probe import probe_adapter

__all__ = [
    "_probe_command",
]


def _probe_command(command) -> UpstreamCommandResult:
    status = probe_adapter(command.key)
    return UpstreamCommandResult(
        key=command.key,
        command=command.description,
        returncode=0 if status.available else 1,
        stdout=status.detail,
        stderr="" if status.available else status.install_hint,
    )
