from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence

from ..adapter_models import AGENT_PROFILES, AgentProfile

__all__ = [
    "_clean_version",
    "default_runner",
    "get_agent_profile",
]


def get_agent_profile(agent: str) -> AgentProfile:
    try:
        return AGENT_PROFILES[agent]
    except KeyError as exc:
        supported = ", ".join(sorted(AGENT_PROFILES))
        raise ValueError(f"Unsupported agent {agent!r}. Supported agents: {supported}") from exc


def default_runner(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _clean_version(output: str) -> str | None:
    value = output.strip()
    if not value:
        return None
    return value.splitlines()[0].strip()
