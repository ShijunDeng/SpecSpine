from __future__ import annotations

from pathlib import Path
from typing import Any

from ..dependency import topological_sort
from ..features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    _extract_markdown_section,
    _extract_markdown_section_lines,
    feature_bundle_paths,
    get_feature_status,
    parse_acceptance_criteria,
    parse_feature_tasks,
    parse_quality_checks,
    parse_test_coverage,
    parse_test_plan,
    read_feature_metadata,
    validate_feature_slug,
)

from .executor_models import ExecutionPlan, GradingRubric


def _parse_task_dependencies(text: str) -> list[str]:
    from .executor_models import TASK_DEP_PATTERN
    return TASK_DEP_PATTERN.findall(text)


def _read_feature_contents(root: Path, slug: str) -> dict[str, str]:
    paths = feature_bundle_paths(root, slug)
    contents: dict[str, str] = {}
    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
    return contents


def _build_steps_from_contents(
    contents: dict[str, str],
    slug: str,
    relative_paths: dict[str, str],
) -> list[dict[str, Any]]:
    execution_content = contents.get("execution", "")
    spec_content = contents.get("spec", "")
    quality_content = contents.get("quality", "")

    ac_items = parse_acceptance_criteria(spec_content, source_file=relative_paths.get("spec", "")) if spec_content else ()
    task_items = parse_feature_tasks(execution_content, source_file=relative_paths.get("execution", "")) if execution_content else ()
    quality_items = parse_quality_checks(quality_content, source_file=relative_paths.get("quality", "")) if quality_content else ()

    ac_by_id: dict[str, dict[str, Any]] = {}
    for ac in ac_items:
        ac_by_id[ac.id] = {
            "id": ac.id,
            "text": ac.text,
            "done": ac.done,
        }

    task_dep_map: dict[str, list[str]] = {}
    for task in task_items:
        deps = _parse_task_dependencies(task.text)
        task_dep_map[task.id] = deps

    source_files: list[str] = []
    for kind, rel_path in relative_paths.items():
        if kind in contents:
            source_files.append(rel_path)

    steps: list[dict[str, Any]] = []
    for task in task_items:
        mapped_ac_ids: list[str] = []
        for ac_id, ac_info in ac_by_id.items():
            if ac_info["text"].lower() in task.text.lower() or task.text.lower() in ac_info["text"].lower():
                mapped_ac_ids.append(ac_id)

        dep_step_ids = []
        for dep in task_dep_map.get(task.id, []):
            dep_step_ids.append(dep)

        ac_texts = [ac_by_id[aid]["text"] for aid in mapped_ac_ids if aid in ac_by_id]

        steps.append({
            "step_id": task.id,
            "description": task.text,
            "mapped_ac_ids": mapped_ac_ids,
            "dependency_step_ids": dep_step_ids,
            "source_files": list(source_files),
            "verification_command": f"specspine verify matrix {slug} . --json",
            "acceptance_criteria_text": ac_texts,
            "done": task.done,
        })

    return steps


def _topo_sort_steps(steps: list[dict[str, Any]]) -> list[str]:
    if not steps:
        return []
    nodes = [{"slug": s["step_id"]} for s in steps]
    edges: list[dict[str, str]] = []
    step_ids = {s["step_id"] for s in steps}
    for s in steps:
        for dep in s["dependency_step_ids"]:
            if dep in step_ids:
                edges.append({"from": dep, "to": s["step_id"]})
    order = topological_sort(nodes, edges)
    if order is not None:
        return order
    return [s["step_id"] for s in steps]


def _build_verification_commands(slug: str) -> list[str]:
    return [
        f"specspine verify matrix {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature ready {slug} . --json --require-coverage",
        f"specspine consistency scan . --feature {slug} --json",
        "specspine validate . --fusion --features",
    ]


def _build_grading_rubric_internal(
    contents: dict[str, str],
    slug: str,
    root: Path,
    relative_paths: dict[str, str],
) -> list[dict[str, Any]]:
    spec_content = contents.get("spec", "")
    quality_content = contents.get("quality", "")

    ac_items = parse_acceptance_criteria(spec_content, source_file=relative_paths.get("spec", "")) if spec_content else ()
    coverage_links = parse_test_coverage(quality_content, source_file=relative_paths.get("quality", ""), root=root) if quality_content else ()
    quality_items = parse_quality_checks(quality_content, source_file=relative_paths.get("quality", "")) if quality_content else ()

    coverage_by_ac: dict[str, list[dict[str, Any]]] = {}
    for link in coverage_links:
        coverage_by_ac.setdefault(link.acceptance_criterion_id, []).append({
            "done": link.done,
            "target_exists": link.target_exists,
            "target_path": link.target_path,
        })

    quality_by_ac: dict[str, list[dict[str, Any]]] = {}
    for item in quality_items:
        quality_by_ac.setdefault("all", []).append({
            "id": item.id,
            "done": item.done,
            "text": item.text,
        })

    rubric_items: list[dict[str, Any]] = []
    for ac in ac_items:
        ac_coverage = coverage_by_ac.get(ac.id, [])
        coverage_complete = any(
            c["done"] and c["target_exists"] for c in ac_coverage
        ) if ac_coverage else False
        has_any_valid_coverage = any(
            c["target_exists"] for c in ac_coverage
        ) if ac_coverage else False

        if ac.done and coverage_complete:
            status = "pass"
        elif ac.done and has_any_valid_coverage:
            status = "warn"
        elif ac.done:
            status = "fail"
        elif coverage_complete:
            status = "warn"
        elif has_any_valid_coverage:
            status = "warn"
        else:
            status = "fail"

        gap_reason = ""
        if status == "fail":
            gap_reason = "No test coverage links found for this AC."
        elif status == "warn":
            gap_reason = "Coverage links exist but are incomplete or unchecked."

        rubric_items.append({
            "ac_id": ac.id,
            "ac_text": ac.text,
            "check_type": "acceptance_criterion",
            "pass_criteria": f"AC {ac.id} is checked and has at least one completed test coverage link.",
            "current_status": status,
            "gap_reason": gap_reason,
        })

    quality_checks_total = len(quality_items)
    quality_checks_done = sum(1 for item in quality_items if item.done)

    if quality_checks_total > 0:
        q_status = "pass" if quality_checks_done == quality_checks_total else "warn"
        rubric_items.append({
            "ac_id": "QUALITY_CHECKS",
            "ac_text": f"{quality_checks_done}/{quality_checks_total} quality checks done",
            "check_type": "quality_gates",
            "pass_criteria": "All required quality checks must be completed.",
            "current_status": q_status,
            "gap_reason": "" if q_status == "pass" else f"{quality_checks_total - quality_checks_done} quality checks remain open.",
        })

    return rubric_items


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


__all__ = [
    "_build_grading_rubric_internal",
    "_build_steps_from_contents",
    "_build_verification_commands",
    "_parse_task_dependencies",
    "_read_feature_contents",
    "_topo_sort_steps",
    "build_execution_plan",
    "build_grading_rubric",
]
