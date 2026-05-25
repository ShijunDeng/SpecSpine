from __future__ import annotations

from .evolution_classification_models import ClassifiedChange
from ._classification_ac_detector import _detect_ac_changes
from ._classification_task_detector import _detect_task_changes

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

    ac_changes, change_counter = _detect_ac_changes(
        before, after, rel_path, change_counter
    )
    changes.extend(ac_changes)

    task_changes, change_counter = _detect_task_changes(
        before, after, rel_path, change_counter
    )
    changes.extend(task_changes)

    return changes, change_counter
