from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_loop_json",
    "render_loop_text",
]


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
