from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import validate_feature_slug

from .executor_models import ExecutionLoopResult
from .executor_plan import build_execution_plan
from ._loop_iteration import _grade_rubric, _build_iteration_summary


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
        grade_results, new_gaps = _grade_rubric(rubric)

        iteration_summary = _build_iteration_summary(
            iteration_num, steps, grade_results, new_gaps,
        )
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
