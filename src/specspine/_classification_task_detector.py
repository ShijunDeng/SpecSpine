from __future__ import annotations

from .evolution_classification_models import ClassifiedChange
from .evolution_classification_helpers import (
    _extract_task_ids,
    _find_line_number,
)

__all__ = [
    "_detect_task_changes",
]


def _detect_task_changes(
    before: str,
    after: str,
    rel_path: str,
    change_counter: int,
) -> tuple[list[ClassifiedChange], int]:
    changes: list[ClassifiedChange] = []

    before_tasks = set(_extract_task_ids(before or ""))
    after_tasks = set(_extract_task_ids(after or ""))

    for task_id in sorted(after_tasks - before_tasks):
        change_counter += 1
        line = _find_line_number(after or "", task_id)
        changes.append(
            ClassifiedChange(
                change_id=f"CHG{change_counter:03d}",
                change_type="added",
                category="task",
                file=rel_path,
                line=line,
                before=None,
                after=task_id,
            )
        )

    for task_id in sorted(before_tasks - after_tasks):
        change_counter += 1
        line = _find_line_number(before or "", task_id)
        changes.append(
            ClassifiedChange(
                change_id=f"CHG{change_counter:03d}",
                change_type="removed",
                category="task",
                file=rel_path,
                line=line,
                before=task_id,
                after=None,
            )
        )

    return changes, change_counter
