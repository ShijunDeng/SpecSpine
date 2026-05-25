from __future__ import annotations

__all__ = [
    "render_orchestration_text",
]


def render_orchestration_text(report) -> str:
    lines: list[str] = []
    lines.append(f"Orchestration plan: {report.root}")
    if report.feature_filter:
        lines.append(f"Feature filter: {report.feature_filter}")
    lines.append(f"Status: {report.status}")
    lines.append("")

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

    if report.integration_recommendations:
        lines.append("Integration recommendations:")
        for rec in report.integration_recommendations:
            lines.append(f"  - {rec}")
    lines.append("")

    if report.blocking_items:
        lines.append("Blocking items:")
        for item in report.blocking_items:
            lines.append(f"  - {item}")
    else:
        lines.append("Blocking items: (none)")
    lines.append("")

    lines.append("Safety notes:")
    for note in report.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"
