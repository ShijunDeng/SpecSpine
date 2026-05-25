from __future__ import annotations

from .feature_bundle import FeatureHandoffReport

__all__ = [
    "_render_handoff_sections",
]


def _render_handoff_sections(report: FeatureHandoffReport) -> list[str]:
    lines = ["Sources:"]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(["", "Next actions:"])
    if report.next_actions:
        lines.extend(f"- {action}" for action in report.next_actions)
    else:
        lines.append("- None.")

    open_tasks = tuple(task for task in report.tasks if not task.done)
    lines.extend(["", "Open tasks:"])
    if open_tasks:
        lines.extend(
            f"- {task.id} {task.source_file}:{task.line} {task.text}"
            for task in open_tasks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Blocking checks:"])
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Key commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)
    return lines
