from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    get_feature_status,
    validate_feature_slug,
)

from ._plan_content_loader import load_plan_context


def build_execution_plan(slug: str, root: Path) -> dict[str, Any]:
    context = load_plan_context(slug, root)

    from .executor_steps import (
        _build_steps_from_contents,
        _build_verification_commands,
    )
    from ._plan_step_assembler import assemble_ordered_steps, compute_step_summary
    from .executor_rubric import _build_grading_rubric_internal
    from ..features import parse_acceptance_criteria
    from .executor_models import ExecutionPlan

    steps = _build_steps_from_contents(
        context["contents"], context["slug"], context["relative_paths"],
    )
    ordered_steps, dependency_order = assemble_ordered_steps(steps)

    verification_commands = _build_verification_commands(context["slug"])

    rubric_items = _build_grading_rubric_internal(
        context["contents"], context["slug"], context["resolved_root"], context["relative_paths"],
    )
    rubric_pass = sum(1 for r in rubric_items if r["current_status"] == "pass")
    rubric_total = len(rubric_items)

    ac_count = len(
        parse_acceptance_criteria(
            context["contents"].get("spec", ""),
            source_file=context["relative_paths"].get("spec", ""),
        ) if context["contents"].get("spec") else ()
    )

    summary = compute_step_summary(
        ordered_steps, steps, ac_count, rubric_pass, rubric_total,
    )

    plan = ExecutionPlan(
        root=str(context["resolved_root"]),
        feature_id=context["feature_id"],
        feature_status=context["feature_status"],
        plan_steps=ordered_steps,
        dependency_order=dependency_order,
        verification_commands=verification_commands,
        grading_rubric={
            "feature_id": context["feature_id"],
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
    "build_execution_plan",
]
