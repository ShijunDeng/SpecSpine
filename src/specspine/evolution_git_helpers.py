from __future__ import annotations

import subprocess
from pathlib import Path

from .features import feature_bundle_paths
from .evolution_git_models import DiffFileHunk

__all__ = [
    "_run_git",
    "_get_peer_files",
    "_parse_diff_hunks",
    "_count_lines_in_hunks",
    "_relative_path",
]


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=30,
    )


def _get_peer_files(slug: str, root: Path) -> dict[str, Path]:
    paths = feature_bundle_paths(root, slug)
    return {
        kind: path
        for kind, path in paths.items()
        if path.exists()
    }


def _parse_diff_hunks(raw_diff: str) -> list[str]:
    hunks: list[str] = []
    current_hunk: list[str] = []
    for line in raw_diff.splitlines():
        if line.startswith("@@"):
            if current_hunk:
                hunks.append("\n".join(current_hunk))
            current_hunk = [line]
        else:
            current_hunk.append(line)
    if current_hunk:
        hunks.append("\n".join(current_hunk))
    return hunks


def _count_lines_in_hunks(hunks: list[str]) -> tuple[int, int]:
    added = 0
    removed = 0
    for hunk in hunks:
        for line in hunk.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1
    return added, removed


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
