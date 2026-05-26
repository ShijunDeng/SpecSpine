from __future__ import annotations

__all__ = [
    "_render_text_conflicts",
]


def _render_text_conflicts(report, lines: list[str]) -> None:
    lines.append(f"Conflicts ({len(report.conflicts)}):")
    if report.conflicts:
        for conflict in report.conflicts:
            lines.append(
                f"  - [{conflict.severity}] {conflict.conflict_type}: {conflict.description}"
            )
            if conflict.affected_files:
                lines.append(f"    files: {', '.join(conflict.affected_files)}")
            lines.append(f"    features: {', '.join(conflict.features_involved)}")
    else:
        lines.append("  (none)")
    lines.append("")
