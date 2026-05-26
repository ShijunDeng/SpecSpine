from __future__ import annotations

__all__ = [
    "_render_text_plan",
]


def _render_text_plan(report, lines: list[str]) -> None:
    plan = report.plan
    lines.append("Execution plan:")
    if plan.execution_order:
        lines.append(f"  order: {' -> '.join(plan.execution_order)}")
    else:
        lines.append("  order: (none)")

    if plan.parallel_groups:
        lines.append("  parallel groups:")
        for group in plan.parallel_groups:
            lines.append(f"    group {group.group_id}: {', '.join(group.features)}")
    else:
        lines.append("  parallel groups: (none)")

    if plan.blocked_features:
        lines.append(f"  blocked: {', '.join(plan.blocked_features)}")
    lines.append(f"  safe_for_parallel: {plan.safe_for_parallel}")
    lines.append("")
