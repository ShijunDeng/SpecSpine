from __future__ import annotations

from typing import Any

__all__ = [
    "render_plan_text",
]


def render_plan_text(result: dict[str, Any]) -> str:
    lines = [
        f"Execution plan: {result['feature_id']}",
        f"Status: {result['feature_status']}",
        "",
        f"Summary: "
        f"steps={result['summary']['total_steps']} "
        f"blocked={result['summary']['blocked_steps']} "
        f"completed={result['summary']['completed_steps']} "
        f"ac={result['summary']['acceptance_criteria']}",
        "",
        "Dependency order: " + " -> ".join(result["dependency_order"]) if result["dependency_order"] else "Dependency order: (none)",
        "",
        "Steps:",
    ]

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

    if result.get("blocked_steps", 0) > 0:
        lines.append("")
        lines.append("Blocked steps:")
        for step in result["plan_steps"]:
            if step.get("blocked"):
                reason = step.get("blocked_reason", "Unknown dependency.")
                lines.append(f"  - {step['step_id']}: {reason}")

    lines.extend(["", "Verification commands:"])
    for cmd in result.get("verification_commands", []):
        lines.append(f"  - {cmd}")

    rubric = result.get("grading_rubric", {})
    if rubric.get("rubric_items"):
        lines.extend([
            "",
            f"Grading rubric: {rubric.get('pass_count', 0)}/{rubric.get('total_count', 0)} pass",
        ])
        for item in rubric["rubric_items"]:
            status = item["current_status"]
            lines.append(f"  - [{status}] {item['ac_id']}: {item['ac_text']}")

    lines.extend(["", "Safety notes:"])
    for note in result.get("safety_notes", ()):
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"
