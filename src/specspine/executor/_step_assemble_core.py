from __future__ import annotations

from typing import Any


def _assemble_steps(
    task_items,
    ac_by_id: dict[str, dict[str, Any]],
    task_dep_map: dict[str, list[str]],
    source_files: list[str],
    slug: str,
) -> list[dict[str, Any]]:
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


__all__ = [
    "_assemble_steps",
]
