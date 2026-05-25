from __future__ import annotations

__all__ = [
    "parse_log_entries",
    "parse_diff_stats",
]


def parse_log_entries(
    lines: list[str],
    limit: int = 20,
) -> list[tuple[str, str, str, str]]:
    entries: list[tuple[str, str, str, str]] = []
    for line in lines[:limit]:
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, date, author, message = parts
        entries.append((commit_hash, date, author, message))
    return entries


def parse_diff_stats(diff_lines: list[str]) -> tuple[int, list[str]]:
    if not diff_lines:
        return 0, ["unknown"]

    change_count = len([l for l in diff_lines if "|" in l])
    summary_line = diff_lines[-1] if diff_lines else ""
    categories = _classify_changes(summary_line)

    return change_count, categories


def _classify_changes(summary_line: str) -> list[str]:
    categories = []
    if "insertion" in summary_line or "add" in summary_line.lower():
        categories.append("added")
    if "deletion" in summary_line or "remove" in summary_line.lower():
        categories.append("removed")
    if not categories:
        categories.append("modified")
    return categories
