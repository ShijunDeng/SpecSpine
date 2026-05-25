from __future__ import annotations

from pathlib import Path
from typing import Any

__all__ = [
    "_fetch_git_log_lines",
]


def _fetch_git_log_lines(root: Path, rel_paths: list[str]) -> list[dict[str, str]]:
    from ..evolution import _run_git

    results: list[dict[str, str]] = []

    git_args = ["log", "--format=%H|%ai|%s", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return results

    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 2)
        if len(parts) < 2:
            continue
        commit_hash, date_str = parts[0], parts[1]
        message = parts[2] if len(parts) > 2 else ""
        results.append({
            "commit_hash": commit_hash,
            "date_str": date_str.strip(),
            "message": message,
        })

    return results
