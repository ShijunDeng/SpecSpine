from __future__ import annotations

from pathlib import Path

from .evolution_git import _get_peer_files, _relative_path, _run_git
from .features import validate_feature_slug
from ._evolution_models import EvolutionEntry

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

    entries: list[EvolutionEntry] = []
    for line in result.stdout.strip().splitlines()[:limit]:
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, date, author, message = parts

        diff_args = ["diff", "--stat", f"{commit_hash}^..{commit_hash}", "--"] + paths
        diff_result = _run_git(diff_args, resolved_root)
        if diff_result.returncode == 0 and diff_result.stdout.strip():
            lines = diff_result.stdout.strip().splitlines()
            change_count = len([l for l in lines if "|" in l])
            summary_line = lines[-1] if lines else ""
            categories = []
            if "insertion" in summary_line or "add" in summary_line.lower():
                categories.append("added")
            if "deletion" in summary_line or "remove" in summary_line.lower():
                categories.append("removed")
            if not categories:
                categories.append("modified")
        else:
            change_count = 0
            categories = ["unknown"]

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
