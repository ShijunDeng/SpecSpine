from __future__ import annotations

from pathlib import Path

from ..evolution_git_models import DiffFileHunk
from ..evolution_git_helpers import (
    _count_lines_in_hunks,
    _parse_diff_hunks,
    _relative_path,
    _run_git,
)

__all__ = [
    "_process_file_diff",
]


def _process_file_diff(
    file_path: Path,
    root: Path,
    *,
    base: str | None = None,
    unstaged: bool = False,
) -> DiffFileHunk:
    rel_path = _relative_path(file_path, root)
    git_args: list[str] = ["diff"]
    if base is not None:
        base_result = _run_git(["rev-parse", "--verify", base], root)
        if base_result.returncode != 0:
            from ..evolution_git_models import InvalidGitBaseError
            raise InvalidGitBaseError(
                f"Invalid git base reference: {base}"
            )
        git_args.append(base)
    if unstaged:
        git_args.append("--")
    git_args.append(rel_path)

    result = _run_git(git_args, root)
    if result.returncode == 0 and result.stdout.strip():
        hunks = _parse_diff_hunks(result.stdout)
        added, removed = _count_lines_in_hunks(hunks)
        return DiffFileHunk(
            path=rel_path,
            diff_hunks=hunks,
            added_lines=added,
            removed_lines=removed,
            modified_lines=added + removed,
        )
    return DiffFileHunk(
        path=rel_path,
        diff_hunks=[],
        added_lines=0,
        removed_lines=0,
        modified_lines=0,
    )
