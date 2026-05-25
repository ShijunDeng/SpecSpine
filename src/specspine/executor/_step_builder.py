from __future__ import annotations

from typing import Any

from ..dependency import topological_sort
from ..features import (
    parse_acceptance_criteria,
    parse_feature_tasks,
    parse_quality_checks,
)

from ._step_parser import _parse_task_dependencies

__all__ = [
    "_build_steps_from_contents",
    "_topo_sort_steps",
]


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
