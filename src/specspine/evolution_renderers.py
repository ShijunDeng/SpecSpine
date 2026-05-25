from __future__ import annotations

import json

__all__ = [
    "render_evolution_json",
    "render_evolution_text",
]


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
