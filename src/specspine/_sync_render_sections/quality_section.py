from __future__ import annotations

from ..feature_bundle import FeatureSyncPlan

__all__ = [
    "_render_gap_lines",
    "_render_blocking_lines",
]


def _render_gap_lines(plan: FeatureSyncPlan) -> list[str]:
    lines = ["", "## Gaps", ""]
    if plan.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in plan.gaps
        )
    else:
        lines.append("- None.")
    return lines


def _render_blocking_lines(plan: FeatureSyncPlan) -> list[str]:
    lines = ["", "## Blocking Checks", ""]
    if plan.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in plan.blocking_checks
        )
    else:
        lines.append("- None.")
    return lines
