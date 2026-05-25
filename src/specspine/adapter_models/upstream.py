from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

__all__ = [
    "CommandRunner",
    "AdapterStatus",
    "UpstreamCommand",
    "UpstreamCommandResult",
]

CommandRunner = Callable[[Sequence[str], Path], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class AdapterStatus:
    key: str
    display_name: str
    available: bool
    detail: str
    version: str | None
    command: str | None
    install_hint: str
    upstream_url: str


@dataclass(frozen=True)
class UpstreamCommand:
    key: str
    description: str
    args: tuple[str, ...]

    def display(self) -> str:
        return " ".join(self.args)


@dataclass(frozen=True)
class UpstreamCommandResult:
    key: str
    command: str
    returncode: int
    stdout: str
    stderr: str
