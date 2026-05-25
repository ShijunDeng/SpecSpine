from __future__ import annotations

from .evolution_classification_models import ClassifiedChange
from .evolution_classification_helpers import (
    _extract_ac_ids,
    _extract_task_ids,
    _find_line_number,
)

__all__ = [
    "_classify_ac_task_changes",
]


def _classify_ac_task_changes(
    before: str,
    after: str,
    rel_path: str,
    change_counter: int,
) -> tuple[list[ClassifiedChange], int]:
    changes: list[ClassifiedChange] = []

    before_ac = set(_extract_ac_ids(before or ""))
    after_ac = set(_extract_ac_ids(after or ""))
    before_tasks = set(_extract_task_ids(before or ""))
    after_tasks = set(_extract_task_ids(after or ""))

    for ac_id in sorted(after_ac - before_ac):
        change_counter += 1
        line = _find_line_number(after or "", ac_id)
        changes.append(
            ClassifiedChange(
                change_id=f"CHG{change_counter:03d}",
                change_type="added",
                category="ac",
                file=rel_path,
                line=line,
                before=None,
                after=ac_id,
            )
        )

    for ac_id in sorted(before_ac - after_ac):
        change_counter += 1
        line = _find_line_number(before or "", ac_id)
        changes.append(
            ClassifiedChange(
                change_id=f"CHG{change_counter:03d}",
                change_type="removed",
                category="ac",
                file=rel_path,
                line=line,
                before=ac_id,
                after=None,
            )
        )

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
