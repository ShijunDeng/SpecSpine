from __future__ import annotations

import subprocess
from pathlib import Path

__all__ = [
    "_run_git",
]


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=30,
    )
