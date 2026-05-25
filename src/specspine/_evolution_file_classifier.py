from __future__ import annotations

from .features import FEATURE_FILE_PATHS
from .evolution_git import DiffResult
from .evolution_classification_models import ClassifiedChange
from .evolution_classification_file_changes import (
    _classify_added_file,
    _classify_removed_file,
)
from .evolution_classification_modified import (
    _classify_modified_file,
)

__all__ = [
    "_classify_file_changes",
]


def _classify_file_changes(
    base_contents: dict[str, str | None],
    current_contents: dict[str, str | None],
    slug: str,
    change_counter: int,
    diff_result: DiffResult,
) -> tuple[list[ClassifiedChange], int]:
    changes: list[ClassifiedChange] = []

    for kind in ("spec", "execution", "quality"):
        rel_path = FEATURE_FILE_PATHS[kind].format(slug=slug)
        before = base_contents.get(kind)
        after = current_contents.get(kind)

        if before is None and after is None:
            continue

        if before is None and after is not None:
            added_changes, change_counter = _classify_added_file(
                after, rel_path, change_counter
            )
            changes.extend(added_changes)
            continue

        if before is not None and after is None:
            removed_changes, change_counter = _classify_removed_file(
                before, rel_path, change_counter
            )
            changes.extend(removed_changes)
            continue

        modified_changes, change_counter = _classify_modified_file(
            before or "", after or "", rel_path, change_counter, diff_result, kind
        )
        changes.extend(modified_changes)

    return changes, change_counter
