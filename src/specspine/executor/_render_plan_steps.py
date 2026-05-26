from __future__ import annotations

from typing import Any

__all__ = [
    "_render_plan_steps_lines",
    "_render_blocked_steps_lines",
]


def _render_plan_steps_lines(result: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for step in result["plan_steps"]:
        blocked = step.get("blocked", False)
        marker = "BLOCKED" if blocked else "READY"
        dep_info = ""
        if step.get("dependency_step_ids"):
            dep_info = f" deps={','.join(step['dependency_step_ids'])}"
        ac_info = ""
        if step.get("mapped_ac_ids"):
            ac_info = f" ac={','.join(step['mapped_ac_ids'])}"
        lines.append(
            f"  - [{marker}] {step['step_id']}{dep_info}{ac_info}: {step['description']}"
        )
    return lines


def _render_blocked_steps_lines(result: dict[str, Any]) -> list[str]:
    if result.get("blocked_steps", 0) <= 0:
        return []
    lines = ["", "Blocked steps:"]
    for step in result["plan_steps"]:
        if step.get("blocked"):
            reason = step.get("blocked_reason", "Unknown dependency.")
            lines.append(f"  - {step['step_id']}: {reason}")
    return lines
