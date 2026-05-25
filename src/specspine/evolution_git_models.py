from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DiffFileHunk",
    "DiffResult",
    "GitDiffError",
    "InvalidGitBaseError",
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
