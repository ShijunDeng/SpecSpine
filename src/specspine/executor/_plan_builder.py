from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    get_feature_status,
    parse_acceptance_criteria,
    validate_feature_slug,
)

from .executor_models import ExecutionPlan
from .executor_steps import (
    _build_steps_from_contents,
    _build_verification_commands,
    _read_feature_contents,
)
from .executor_rubric import _build_grading_rubric_internal
from ._plan_step_assembler import assemble_ordered_steps, compute_step_summary

__all__ = [
    "build_execution_plan",
]


def build_execution_plan(slug: str, root: Path) -> dict[str, Any]:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    relative_paths = {
        kind: pattern.format(slug=slug)
        for kind, pattern in FEATURE_FILE_PATHS.items()
    }

    status_report = get_feature_status(resolved_root, feature_id)
    feature_status = status_report.status or "unknown"

    contents = _read_feature_contents(resolved_root, feature_id)
    if not contents:
        missing = [relative_paths[k] for k in FEATURE_FILE_PATHS]
        raise FeatureBundleNotFoundError(
            slug=feature_id,
            root=resolved_root,
            missing_paths=tuple(resolved_root / p for p in missing),
        )

    steps = _build_steps_from_contents(contents, slug, relative_paths)
    ordered_steps, dependency_order = assemble_ordered_steps(steps)

    verification_commands = _build_verification_commands(slug)

    rubric_items = _build_grading_rubric_internal(contents, slug, resolved_root, relative_paths)
    rubric_pass = sum(1 for r in rubric_items if r["current_status"] == "pass")
    rubric_total = len(rubric_items)

    ac_count = len(
        parse_acceptance_criteria(
            contents.get("spec", ""),
            source_file=relative_paths.get("spec", ""),
        ) if contents.get("spec") else ()
    )

    summary = compute_step_summary(
        ordered_steps, steps, ac_count, rubric_pass, rubric_total,
    )

    plan = ExecutionPlan(
        root=str(resolved_root),
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
