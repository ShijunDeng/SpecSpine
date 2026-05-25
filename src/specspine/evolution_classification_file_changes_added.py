from __future__ import annotations

from .evolution_classification_models import (
    AC_ID_RE,
    TASK_ID_RE,
    ClassifiedChange,
)
from .evolution_classification_helpers import (
    _parse_section_ids,
)

__all__ = [
    "_classify_added_file",
]


def _classify_added_file(
    after: str,
    rel_path: str,
    change_counter: int,
) -> tuple[list[ClassifiedChange], int]:
    changes: list[ClassifiedChange] = []
    ac_ids = _parse_section_ids(after, AC_ID_RE)
    for ac_id, line in ac_ids:
        change_counter += 1
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
    task_ids = _parse_section_ids(after, TASK_ID_RE)
    for task_id, line in task_ids:
        change_counter += 1
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
    return changes, change_counter
