from __future__ import annotations

__all__ = [
    "_parse_diff_hunks",
    "_count_lines_in_hunks",
]


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
