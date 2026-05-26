from __future__ import annotations

__all__ = [
    "_render_issue_files",
]


def _render_issue_files(
    *,
    source_files: tuple[str, ...],
    missing_files: tuple[str, ...],
) -> list[str]:
    lines: list[str] = [
        "## Source Files",
        "",
    ]

    lines.extend(f"- {relative_path}" for relative_path in source_files)
    lines.extend(["", "## Missing Files", ""])
    if missing_files:
        lines.append(
            "This draft was generated from an incomplete feature bundle. "
            "Add these files before treating the issue as ready:"
        )
        lines.append("")
        lines.extend(f"- {relative_path}" for relative_path in missing_files)
    else:
        lines.append("None.")

    return lines
