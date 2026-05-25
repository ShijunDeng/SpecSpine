from __future__ import annotations

from typing import Any

from ..features import parse_acceptance_criteria


def compute_plan_metrics(
    contents: dict[str, str],
    relative_paths: dict[str, str],
) -> int:
    return len(
        parse_acceptance_criteria(
            contents.get("spec", ""),
            source_file=relative_paths.get("spec", ""),
        ) if contents.get("spec") else ()
    )


def compute_rubric_metrics(
    rubric_items: list[dict[str, Any]],
) -> tuple[int, int]:
    rubric_pass = sum(1 for r in rubric_items if r["current_status"] == "pass")
    rubric_total = len(rubric_items)
    return rubric_pass, rubric_total


__all__ = [
    "compute_plan_metrics",
    "compute_rubric_metrics",
]
