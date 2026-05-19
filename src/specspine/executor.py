from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .dependency import topological_sort
from .features import (
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

CHECKBOX_TASK_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
AC_ID_RE = re.compile(r"\bAC\d{3,}\b", re.IGNORECASE)
DEP_PATTERN = re.compile(
    r"(?:depends\s+on|after|blocked\s+by|requires|prerequisite:\s*)"
    r"([a-z0-9]+(?:-[a-z0-9]+)*)",
    re.IGNORECASE,
)
TASK_DEP_PATTERN = re.compile(
    r"(?:after|depends\s+on|blocked\s+by)\s+([Tt]\d{3,})",
    re.IGNORECASE,
)


def _parse_task_dependencies(text: str) -> list[str]:
    return TASK_DEP_PATTERN.findall(text)


def _read_feature_contents(root: Path, slug: str) -> dict[str, str]:
    paths = feature_bundle_paths(root, slug)
    contents: dict[str, str] = {}
    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
    return contents


@dataclass(frozen=True)
class ExecutionPlan:
    root: str
    feature_id: str
    feature_status: str
    plan_steps: list[dict[str, Any]]
    dependency_order: list[str]
    verification_commands: list[str]
    grading_rubric: dict[str, Any]
    summary: dict[str, Any]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "dependency_order": list(self.dependency_order),
            "feature_id": self.feature_id,
            "feature_status": self.feature_status,
            "grading_rubric": dict(self.grading_rubric),
            "plan_steps": [dict(s) for s in self.plan_steps],
            "root": self.root,
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
            "verification_commands": list(self.verification_commands),
        }


@dataclass(frozen=True)
class GradingRubric:
    feature_id: str
    rubric_items: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "rubric_items": [dict(item) for item in self.rubric_items],
        }


@dataclass(frozen=True)
class ExecutionLoopResult:
    feature_id: str
    iterations: list[dict[str, Any]]
    final_status: str
    remaining_gaps: list[dict[str, str]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "final_status": self.final_status,
            "iterations": [dict(it) for it in self.iterations],
            "remaining_gaps": [dict(g) for g in self.remaining_gaps],
        }


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


def render_plan_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def render_plan_text(result: dict[str, Any]) -> str:
    lines = [
        f"Execution plan: {result['feature_id']}",
        f"Status: {result['feature_status']}",
        "",
        f"Summary: "
        f"steps={result['summary']['total_steps']} "
        f"blocked={result['summary']['blocked_steps']} "
        f"completed={result['summary']['completed_steps']} "
        f"ac={result['summary']['acceptance_criteria']}",
        "",
        "Dependency order: " + " -> ".join(result["dependency_order"]) if result["dependency_order"] else "Dependency order: (none)",
        "",
        "Steps:",
    ]

    for step in result["plan_steps"]:
        blocked = step.get("blocked", False)
        marker = "BLOCKED" if blocked else "READY"
        dep_info = ""
        if step.get("dependency_step_ids"):
            dep_info = f" deps={','.join(step['dependency_step_ids'])}"
        ac_info = ""
        if step.get("mapped_ac_ids"):
            ac_info = f" ac={','.join(step['mapped_ac_ids'])}"
        lines.append(
            f"  - [{marker}] {step['step_id']}{dep_info}{ac_info}: {step['description']}"
        )

    if result.get("blocked_steps", 0) > 0:
        lines.append("")
        lines.append("Blocked steps:")
        for step in result["plan_steps"]:
            if step.get("blocked"):
                reason = step.get("blocked_reason", "Unknown dependency.")
                lines.append(f"  - {step['step_id']}: {reason}")

    lines.extend(["", "Verification commands:"])
    for cmd in result.get("verification_commands", []):
        lines.append(f"  - {cmd}")

    rubric = result.get("grading_rubric", {})
    if rubric.get("rubric_items"):
        lines.extend([
            "",
            f"Grading rubric: {rubric.get('pass_count', 0)}/{rubric.get('total_count', 0)} pass",
        ])
        for item in rubric["rubric_items"]:
            status = item["current_status"]
            lines.append(f"  - [{status}] {item['ac_id']}: {item['ac_text']}")

    lines.extend(["", "Safety notes:"])
    for note in result.get("safety_notes", ()):
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"


def render_grade_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def render_grade_text(result: dict[str, Any]) -> str:
    items = result.get("rubric_items", [])
    pass_count = sum(1 for item in items if item["current_status"] == "pass")
    total = len(items)

    lines = [
        f"Grading rubric: {result['feature_id']}",
        f"Score: {pass_count}/{total} pass",
        "",
        "Rubric items:",
    ]

    for item in items:
        status = item["current_status"]
        lines.append(
            f"  - [{status}] {item['ac_id']} ({item['check_type']}): {item['ac_text']}"
        )
        if item.get("gap_reason"):
            lines.append(f"    Gap: {item['gap_reason']}")
        lines.append(f"    Criteria: {item['pass_criteria']}")

    return "\n".join(lines) + "\n"


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
