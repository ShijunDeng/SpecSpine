from __future__ import annotations

__all__ = [
    "_render_pr_trailing_sections",
]


def _render_pr_trailing_sections(
    *,
    gaps: tuple[dict[str, str], ...],
    source_files: tuple[str, ...],
    missing_files: tuple[str, ...],
    recommended_commands: tuple[str, ...],
) -> list[str]:
    lines: list[str] = []

    lines.extend(["", "## Gaps", ""])
    if gaps:
        lines.extend(
            f"- [ ] {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in gaps
        )
    else:
        lines.append("- [x] None.")

    lines.extend(["", "## Source Files", ""])
    if source_files:
        lines.extend(f"- {relative_path}" for relative_path in source_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Missing Files", ""])
    if missing_files:
        lines.extend(f"- [ ] {relative_path}" for relative_path in missing_files)
    else:
        lines.append("- [x] None.")

    lines.extend(["", "## Key Commands", ""])
    lines.extend(f"- `{command}`" for command in recommended_commands)

    return lines
