from __future__ import annotations

from typing import Any

from .executor_models import ExecutionPlan


def construct_execution_plan(
    root: str,
    feature_id: str,
    feature_status: str,
    ordered_steps: list[dict[str, Any]],
    dependency_order: list[str],
    verification_commands: list[dict[str, Any]],
    rubric_items: list[dict[str, Any]],
    rubric_pass: int,
    rubric_total: int,
    summary: dict[str, Any],
) -> dict[str, Any]:
    plan = ExecutionPlan(
        root=root,
        feature_id=feature_id,
        feature_status=feature_status,
        plan_steps=ordered_steps,
        dependency_order=dependency_order,
        verification_commands=verification_commands,
        grading_rubric={
            "feature_id": feature_id,
            "rubric_items": rubric_items,
            "pass_count": rubric_pass,
            "total_count": rubric_total,
        },
        summary=summary,
        safety_notes=(
            "This execution plan is advisory local evidence.",
            "Recommended commands are advisory and are not executed.",
            "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
        ),
    )

    return plan.as_dict()


__all__ = [
    "construct_execution_plan",
]
