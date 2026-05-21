from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    feature_bundle_paths,
    validate_feature_slug,
)

__all__ = [
    "DiffFileHunk",
    "DiffResult",
    "GitDiffError",
    "InvalidGitBaseError",
    "_build_versioned_content",
    "_get_peer_files",
    "_parse_diff_hunks",
    "_relative_path",
    "_run_git",
    "get_git_diff",
]


@dataclass(frozen=True)
class DiffFileHunk:
    path: str
    diff_hunks: list[str]
    added_lines: int
    removed_lines: int
    modified_lines: int

    def as_dict(self) -> dict[str, object]:
        return {
            "added_lines": self.added_lines,
            "diff_hunks": self.diff_hunks,
            "modified_lines": self.modified_lines,
            "path": self.path,
            "removed_lines": self.removed_lines,
        }


@dataclass(frozen=True)
class DiffResult:
    slug: str
    files: list[DiffFileHunk]

    @property
    def summary(self) -> dict[str, int]:
        total_added = sum(f.added_lines for f in self.files)
        total_removed = sum(f.removed_lines for f in self.files)
        total_modified = sum(f.modified_lines for f in self.files)
        return {
            "files_changed": len(self.files),
            "total_added": total_added,
            "total_modified": total_modified,
            "total_removed": total_removed,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "files": [f.as_dict() for f in self.files],
            "slug": self.slug,
            "summary": self.summary,
        }


class GitDiffError(Exception):
    pass


class InvalidGitBaseError(ValueError):
    pass


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
