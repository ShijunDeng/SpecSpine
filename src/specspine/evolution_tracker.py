from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .evolution_git import _get_peer_files, _relative_path, _run_git
from .features import validate_feature_slug

__all__ = [
    "EvolutionEntry",
    "build_evolution_timeline",
    "render_evolution_json",
    "render_evolution_text",
]


@dataclass(frozen=True)
class EvolutionEntry:
    commit_hash: str
    date: str
    author: str
    message: str
    change_count: int
    categories: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "author": self.author,
            "categories": self.categories,
            "change_count": self.change_count,
            "commit_hash": self.commit_hash,
            "date": self.date,
            "message": self.message,
        }


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


def render_evolution_json(result: dict[str, object]) -> str:
    return json.dumps(result, indent=2, sort_keys=False) + "\n"


def render_evolution_text(result: dict[str, object]) -> str:
    lines: list[str] = []
    slug = result.get("slug", "unknown")
    lines.append(f"Evolution timeline for feature '{slug}'")
    lines.append("")

    diff_summary = result.get("diff_summary", {})
    if diff_summary:
        lines.append("Diff Summary:")
        lines.append(
            f"  Files changed: {diff_summary.get('files_changed', 0)}, "
            f"Added: {diff_summary.get('total_added', 0)}, "
            f"Removed: {diff_summary.get('total_removed', 0)}"
        )
        lines.append("")

    classification = result.get("classification", {})
    changes = classification.get("changes", [])
    if changes:
        lines.append(f"Changes ({len(changes)}):")
        for change in changes:
            change_type = change.get("change_type", "unknown")
            category = change.get("category", "unknown")
            file_path = change.get("file", "")
            lines.append(f"  [{change_type}] {category}: {file_path}")
        lines.append("")

    impact = result.get("impact", {})
    impact_summary = impact.get("summary", {})
    if impact_summary.get("total", 0):
        lines.append("Impact Summary:")
        lines.append(
            f"  Total: {impact_summary.get('total', 0)}, "
            f"Breaking: {impact_summary.get('breaking', 0)}, "
            f"Warning: {impact_summary.get('warning', 0)}, "
            f"Info: {impact_summary.get('info', 0)}"
        )
        lines.append("")

    remediation = result.get("remediation", [])
    if remediation:
        lines.append(f"Remediation Actions ({len(remediation)}):")
        for action in remediation:
            lines.append(f"  [P{action['priority']}] {action['description']}")
        lines.append("")

    timeline = result.get("timeline", [])
    if timeline:
        lines.append(f"Timeline ({len(timeline)} commits):")
        for entry in timeline:
            lines.append(
                f"  {entry['commit_hash'][:8]} {entry['date'][:10]} "
                f"{entry['author']}: {entry['message']}"
            )
        lines.append("")

    return "\n".join(lines) + "\n"
