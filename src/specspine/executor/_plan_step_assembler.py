from __future__ import annotations

from typing import Any

from .executor_steps import _topo_sort_steps

__all__ = [
    "assemble_ordered_steps",
    "compute_step_summary",
]


def assemble_ordered_steps(
    steps: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
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

    return ordered_steps, dependency_order


def compute_step_summary(
    ordered_steps: list[dict[str, Any]],
    steps: list[dict[str, Any]],
    ac_count: int,
    rubric_pass: int,
    rubric_total: int,
) -> dict[str, Any]:
    return {
        "total_steps": len(ordered_steps),
        "blocked_steps": sum(1 for s in ordered_steps if s.get("blocked", False)),
        "completed_steps": sum(1 for s in steps if s.get("done", False)),
        "acceptance_criteria": ac_count,
        "rubric_pass": rubric_pass,
        "rubric_total": rubric_total,
    }
