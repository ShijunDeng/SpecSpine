from __future__ import annotations

import json

from .evolution_git import DiffResult

__all__ = [
    "render_diff_json",
    "render_diff_text",
]


def render_diff_json(result: DiffResult) -> str:
    return json.dumps(result.as_dict(), indent=2, sort_keys=False) + "\n"


def render_diff_text(result: DiffResult) -> str:
    lines: list[str] = []
    lines.append(f"Spec diff for feature '{result.slug}'")
    lines.append("")

    summary = result.summary
    lines.append(
        f"Files changed: {summary['files_changed']}, "
        f"Added: {summary['total_added']}, "
        f"Removed: {summary['total_removed']}, "
        f"Modified: {summary['total_modified']}"
    )
    lines.append("")

    if not result.files:
        lines.append("No changes detected.")
        return "\n".join(lines) + "\n"

    for file_hunk in result.files:
        lines.append(f"  {file_hunk.path}")
        lines.append(
            f"    +{file_hunk.added_lines} -{file_hunk.removed_lines} "
            f"~{file_hunk.modified_lines}"
        )
        for hunk in file_hunk.diff_hunks[:5]:
            for hunk_line in hunk.splitlines()[:10]:
                lines.append(f"    {hunk_line}")
            if len(hunk.splitlines()) > 10:
                lines.append("    ...")
        lines.append("")

    return "\n".join(lines) + "\n"
