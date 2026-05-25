from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .evolution import _run_git

GIT_LOG_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

__all__ = [
    "_git_commit",
    "_run_git_log",
    "GIT_LOG_DATE_RE",
]


def _git_commit(root: Path) -> str:
    try:
        result = _run_git(["rev-parse", "HEAD"], root)
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _run_git_log(root: Path, rel_paths: list[str]) -> list[str]:
    git_args = ["log", "--format=%H|%ai|%s", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return []
    return result.stdout.strip().splitlines()
