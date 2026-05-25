from __future__ import annotations

from pathlib import Path

from .evolution_git import _get_peer_files, _relative_path, _run_git

__all__ = [
    "fetch_git_log_lines",
    "fetch_diff_lines",
]


def fetch_git_log_lines(
    resolved_root: Path,
    slug: str,
) -> list[str]:
    peer_files = _get_peer_files(slug, resolved_root)
    if not peer_files:
        return []

    paths = [_relative_path(p, resolved_root) for p in peer_files.values()]
    git_args = [
        "log",
        "--format=%H|%ai|%an|%s",
        "--",
    ] + paths

    result = _run_git(git_args, resolved_root)
    if result.returncode != 0:
        return []

    return result.stdout.strip().splitlines()


def fetch_diff_lines(
    commit_hash: str,
    resolved_root: Path,
    slug: str,
) -> list[str]:
    peer_files = _get_peer_files(slug, resolved_root)
    if not peer_files:
        return []

    paths = [_relative_path(p, resolved_root) for p in peer_files.values()]
    diff_args = ["diff", "--stat", f"{commit_hash}^..{commit_hash}", "--"] + paths

    diff_result = _run_git(diff_args, resolved_root)
    if diff_result.returncode != 0 or not diff_result.stdout.strip():
        return []

    return diff_result.stdout.strip().splitlines()
