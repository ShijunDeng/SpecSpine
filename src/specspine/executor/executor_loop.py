from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import validate_feature_slug

from .executor_models import ExecutionLoopResult
from .executor_plan import build_execution_plan


def run_execution_loop(
    slug: str,
    root: Path,
    max_iterations: int = 3,
) -> dict[str, Any]:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    max_iterations = max(1, min(max_iterations, 10))

    plan = build_execution_plan(slug, root)
    steps = plan["plan_steps"]
    rubric = plan["grading_rubric"]

    iterations: list[dict[str, Any]] = []
    remaining_gaps: list[dict[str, str]] = []
    final_status = "incomplete"

    for iteration_num in range(1, max_iterations + 1):
        plan_steps_completed = [
            s["step_id"] for s in steps if not s.get("blocked", False)
        ]

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

        completed_count = sum(1 for r in grade_results if r["status"] == "pass")
        total_count = len(grade_results)

        iteration_summary = {
            "iteration": iteration_num,
            "plan_steps_completed": plan_steps_completed,
            "grade_results": grade_results,
            "gaps_found": len(new_gaps),
            "pass_count": completed_count,
            "total_count": total_count,
        }
        iterations.append(iteration_summary)

        if not new_gaps:
            final_status = "complete"
            remaining_gaps = []
            break

        remaining_gaps = new_gaps

        if iteration_num < max_iterations:
            pass

    if remaining_gaps and final_status != "complete":
        final_status = "gaps_remaining"

    result = ExecutionLoopResult(
        feature_id=feature_id,
        iterations=iterations,
        final_status=final_status,
        remaining_gaps=remaining_gaps,
    )

    return result.as_dict()


__all__ = [
    "run_execution_loop",
]
