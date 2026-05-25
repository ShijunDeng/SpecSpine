from __future__ import annotations

from pathlib import Path
from typing import Any

from ._plan_content_loader import load_plan_context
from ._plan_orchestrator import compute_plan_metrics, compute_rubric_metrics
from ._plan_constructor import construct_execution_plan


def build_execution_plan(slug: str, root: Path) -> dict[str, Any]:
    context = load_plan_context(slug, root)

    from .executor_steps import (
        _build_steps_from_contents,
        _build_verification_commands,
    )
    from ._plan_step_assembler import assemble_ordered_steps, compute_step_summary
    from .executor_rubric import _build_grading_rubric_internal

    steps = _build_steps_from_contents(
        context["contents"], context["slug"], context["relative_paths"],
    )
    ordered_steps, dependency_order = assemble_ordered_steps(steps)

    verification_commands = _build_verification_commands(context["slug"])

    rubric_items = _build_grading_rubric_internal(
        context["contents"], context["slug"], context["resolved_root"], context["relative_paths"],
    )
    rubric_pass, rubric_total = compute_rubric_metrics(rubric_items)

    ac_count = compute_plan_metrics(context["contents"], context["relative_paths"])

    summary = compute_step_summary(
        ordered_steps, steps, ac_count, rubric_pass, rubric_total,
    )

    return construct_execution_plan(
        root=str(context["resolved_root"]),
        feature_id=context["feature_id"],
        feature_status=context["feature_status"],
        ordered_steps=ordered_steps,
        dependency_order=dependency_order,
        verification_commands=verification_commands,
        rubric_items=rubric_items,
        rubric_pass=rubric_pass,
        rubric_total=rubric_total,
        summary=summary,
    )


__all__ = [
    "build_execution_plan",
]
