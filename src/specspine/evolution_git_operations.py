from __future__ import annotations

from pathlib import Path

from .features import FEATURE_FILE_PATHS, validate_feature_slug
from .evolution_git_models import DiffFileHunk, DiffResult, InvalidGitBaseError
from .evolution_git_helpers import (
    _count_lines_in_hunks,
    _get_peer_files,
    _parse_diff_hunks,
    _relative_path,
    _run_git,
)

__all__ = [
    "get_git_diff",
    "_build_versioned_content",
]


def get_git_diff(
    slug: str,
    root: Path,
    base: str | None = None,
    unstaged: bool = False,
) -> DiffResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    peer_files = _get_peer_files(slug, resolved_root)

    if not peer_files:
        return DiffResult(slug=slug, files=[])

    file_results: list[DiffFileHunk] = []
    for kind, file_path in sorted(peer_files.items()):
        rel_path = _relative_path(file_path, resolved_root)
        git_args: list[str] = ["diff"]
        if base is not None:
            base_result = _run_git(["rev-parse", "--verify", base], resolved_root)
            if base_result.returncode != 0:
                raise InvalidGitBaseError(
                    f"Invalid git base reference: {base}"
                )
            git_args.append(base)
        if unstaged:
            git_args.append("--")
        git_args.append(rel_path)

        result = _run_git(git_args, resolved_root)
        if result.returncode == 0 and result.stdout.strip():
            hunks = _parse_diff_hunks(result.stdout)
            added, removed = _count_lines_in_hunks(hunks)
            file_results.append(
                DiffFileHunk(
                    path=rel_path,
                    diff_hunks=hunks,
                    added_lines=added,
                    removed_lines=removed,
                    modified_lines=added + removed,
                )
            )
        else:
            file_results.append(
                DiffFileHunk(
                    path=rel_path,
                    diff_hunks=[],
                    added_lines=0,
                    removed_lines=0,
                    modified_lines=0,
                )
            )

    return DiffResult(slug=slug, files=file_results)


def _build_versioned_content(
    root: Path,
    slug: str,
    base: str | None = None,
) -> dict[str, str | None]:
    contents: dict[str, str | None] = {}
    for kind in FEATURE_FILE_PATHS:
        rel_path = FEATURE_FILE_PATHS[kind].format(slug=slug)
        file_path = root / rel_path
        if not file_path.exists():
            contents[kind] = None
            continue

        if base is None:
            contents[kind] = file_path.read_text(encoding="utf-8")
        else:
            result = _run_git(
                ["show", f"{base}:{rel_path}"],
                root,
            )
            if result.returncode == 0:
                contents[kind] = result.stdout
            else:
                contents[kind] = None
    return contents
