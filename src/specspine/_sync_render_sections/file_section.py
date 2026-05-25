from __future__ import annotations

from ..feature_bundle import FeatureSyncPlan

__all__ = [
    "_render_source_lines",
]


def _render_source_lines(plan: FeatureSyncPlan) -> list[str]:
    lines = ["", "## Sources", ""]
    if plan.source_files:
        lines.extend(f"- [ok] {relative_path}" for relative_path in plan.source_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Missing Files", ""])
    if plan.missing_files:
        lines.extend(f"- [missing] {relative_path}" for relative_path in plan.missing_files)
    else:
        lines.append("- None.")
    return lines
