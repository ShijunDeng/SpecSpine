from __future__ import annotations

from typing import Any


def _grade_rubric(rubric: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    grade_results: list[dict[str, Any]] = []
    new_gaps: list[dict[str, str]] = []

    for item in rubric.get("rubric_items", []):
        grade_results.append({
            "ac_id": item["ac_id"],
            "status": item["current_status"],
            "check_type": item["check_type"],
        })
        if item["current_status"] != "pass":
            new_gaps.append({
                "id": item["ac_id"],
                "message": item.get("gap_reason", "Check not passing."),
                "check_type": item["check_type"],
            })

    return grade_results, new_gaps


def _build_iteration_summary(
    iteration_num: int,
    steps: list[dict[str, Any]],
    grade_results: list[dict[str, Any]],
    new_gaps: list[dict[str, str]],
) -> dict[str, Any]:
    plan_steps_completed = [
        s["step_id"] for s in steps if not s.get("blocked", False)
    ]
    completed_count = sum(1 for r in grade_results if r["status"] == "pass")
    total_count = len(grade_results)

    return {
        "iteration": iteration_num,
        "plan_steps_completed": plan_steps_completed,
        "grade_results": grade_results,
        "gaps_found": len(new_gaps),
        "pass_count": completed_count,
        "total_count": total_count,
    }


__all__ = [
    "_grade_rubric",
    "_build_iteration_summary",
]
