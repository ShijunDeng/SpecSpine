from __future__ import annotations

import json
from typing import Any


def render_plan_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


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


def render_grade_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def render_grade_text(result: dict[str, Any]) -> str:
    items = result.get("rubric_items", [])
    pass_count = sum(1 for item in items if item["current_status"] == "pass")
    total = len(items)

    lines = [
        f"Grading rubric: {result['feature_id']}",
        f"Score: {pass_count}/{total} pass",
        "",
        "Rubric items:",
    ]

    for item in items:
        status = item["current_status"]
        lines.append(
            f"  - [{status}] {item['ac_id']} ({item['check_type']}): {item['ac_text']}"
        )
        if item.get("gap_reason"):
            lines.append(f"    Gap: {item['gap_reason']}")
        lines.append(f"    Criteria: {item['pass_criteria']}")

    return "\n".join(lines) + "\n"


def render_loop_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def render_loop_text(result: dict[str, Any]) -> str:
    lines = [
        f"Execution loop: {result['feature_id']}",
        f"Final status: {result['final_status']}",
        f"Iterations: {len(result['iterations'])}",
        "",
    ]

    for iteration in result["iterations"]:
        num = iteration["iteration"]
        lines.append(
            f"Iteration {num}: "
            f"pass={iteration['pass_count']}/{iteration['total_count']} "
            f"gaps={iteration['gaps_found']}"
        )
        completed = iteration["plan_steps_completed"]
        if completed:
            lines.append(f"  Steps completed: {', '.join(completed)}")
        for grade in iteration.get("grade_results", []):
            lines.append(f"  [{grade['status']}] {grade['ac_id']} ({grade['check_type']})")
        lines.append("")

    if result["remaining_gaps"]:
        lines.append("Remaining gaps:")
        for gap in result["remaining_gaps"]:
            lines.append(f"  - {gap['id']}: {gap['message']}")
    else:
        lines.append("No remaining gaps.")

    lines.extend([
        "",
        "Safety notes:",
        "  - This execution loop is advisory local evidence.",
        "  - Recommended commands are advisory and are not executed.",
        "  - SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    ])

    return "\n".join(lines) + "\n"


__all__ = [
    "render_grade_json",
    "render_grade_text",
    "render_loop_json",
    "render_loop_text",
    "render_plan_json",
    "render_plan_text",
]
