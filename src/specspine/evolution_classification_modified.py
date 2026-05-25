from __future__ import annotations

from .evolution_classification_models import ClassifiedChange
from ._classification_ac_task_detector import _classify_ac_task_changes
from ._classification_diff_handler import _classify_diff_modifications

__all__ = [
    "_classify_modified_file",
]


def _classify_modified_file(
    before: str,
    after: str,
    rel_path: str,
    change_counter: int,
    diff_result,
    kind: str,
) -> tuple[list[ClassifiedChange], int]:
    changes, change_counter = _classify_ac_task_changes(
        before, after, rel_path, change_counter,
    )

    diff_changes, change_counter = _classify_diff_modifications(
        before, after, rel_path, change_counter, diff_result, kind,
    )
    changes.extend(diff_changes)

    return changes, change_counter
