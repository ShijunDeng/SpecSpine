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

from .executor_models import ExecutionPlan, GradingRubric
from .executor_steps import (
    _build_steps_from_contents,
    _build_verification_commands,
    _read_feature_contents,
    _topo_sort_steps,
)
from .executor_rubric import _build_grading_rubric_internal

__all__ = [
    "build_execution_plan",
    "build_grading_rubric",
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
    dependency_order = _topo_sort_steps(steps)

    ordered_steps: list[dict[str, Any]] = []
    for step_id in dependency_order:
        for step in steps:
            if step["step_id"] == step_id:
                step_copy = {k: v for k, v in step.items() if k != "done"}
                step_copy["blocked"] = False
                blocked_reasons: list[str] = []
                for dep_id in step_copy["dependency_step_ids"]:
                    dep_done = any(
                        s.get("done", False) for s in steps if s["step_id"] == dep_id
                    )
                    if not dep_done:
                        step_copy["blocked"] = True
                        blocked_reasons.append(f"Dependency {dep_id} not completed.")
                if blocked_reasons:
                    step_copy["blocked_reason"] = " ".join(blocked_reasons)
                ordered_steps.append(step_copy)
                break

    verification_commands = _build_verification_commands(slug)

    rubric_items = _build_grading_rubric_internal(contents, slug, resolved_root, relative_paths)
    rubric_pass = sum(1 for r in rubric_items if r["current_status"] == "pass")
    rubric_total = len(rubric_items)

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
        summary={
            "total_steps": len(ordered_steps),
            "blocked_steps": sum(1 for s in ordered_steps if s.get("blocked", False)),
            "completed_steps": sum(1 for s in steps if s.get("done", False)),
            "acceptance_criteria": len(
                parse_acceptance_criteria(
                    contents.get("spec", ""),
                    source_file=relative_paths.get("spec", ""),
                ) if contents.get("spec") else ()
            ),
            "rubric_pass": rubric_pass,
            "rubric_total": rubric_total,
        },
        safety_notes=(
            "This execution plan is advisory local evidence.",
            "Recommended commands are advisory and are not executed.",
            "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
        ),
    )

    return plan.as_dict()


def build_grading_rubric(slug: str, root: Path) -> dict[str, Any]:
    feature_id = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    relative_paths = {
        kind: pattern.format(slug=slug)
        for kind, pattern in FEATURE_FILE_PATHS.items()
    }

    contents = _read_feature_contents(resolved_root, feature_id)
    if not contents:
        missing = [relative_paths[k] for k in FEATURE_FILE_PATHS]
        raise FeatureBundleNotFoundError(
            slug=feature_id,
            root=resolved_root,
            missing_paths=tuple(resolved_root / p for p in missing),
        )

    rubric_items = _build_grading_rubric_internal(contents, slug, resolved_root, relative_paths)

    rubric = GradingRubric(
        feature_id=feature_id,
        rubric_items=rubric_items,
    )

    return rubric.as_dict()
