from __future__ import annotations

from .evolution_classification_models import ClassifiedChange
from .evolution_classification_helpers import (
    _extract_ac_ids,
    _find_line_number,
)

__all__ = [
    "_detect_ac_changes",
]


def _detect_ac_changes(
    before: str,
    after: str,
    rel_path: str,
    change_counter: int,
) -> tuple[list[ClassifiedChange], int]:
    changes: list[ClassifiedChange] = []

    before_ac = set(_extract_ac_ids(before or ""))
    after_ac = set(_extract_ac_ids(after or ""))

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

    return changes, change_counter
