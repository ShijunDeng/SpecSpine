from __future__ import annotations

from pathlib import Path

from .features import validate_feature_slug
from ._evolution_models import EvolutionEntry
from ._timeline_git_ops import fetch_git_log_lines, fetch_diff_lines
from ._timeline_diff_parser import parse_log_entries, parse_diff_stats

__all__ = [
    "build_evolution_timeline",
]


def build_evolution_timeline(
    slug: str,
    root: Path,
    limit: int = 20,
) -> list[EvolutionEntry]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    log_lines = fetch_git_log_lines(resolved_root, slug)
    if not log_lines:
        return []

    log_entries = parse_log_entries(log_lines, limit)

    entries: list[EvolutionEntry] = []
    for commit_hash, date, author, message in log_entries:
        diff_lines = fetch_diff_lines(commit_hash, resolved_root, slug)
        change_count, categories = parse_diff_stats(diff_lines)

        entries.append(
            EvolutionEntry(
                commit_hash=commit_hash,
                date=date,
                author=author,
                message=message,
                change_count=change_count,
                categories=categories,
            )
        )

    return entries
