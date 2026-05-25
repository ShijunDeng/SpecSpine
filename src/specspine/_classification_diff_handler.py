from __future__ import annotations

from .evolution_classification_models import ClassifiedChange

__all__ = [
    "_classify_diff_modifications",
]


def _classify_diff_modifications(
    before: str,
    after: str,
    rel_path: str,
    change_counter: int,
    diff_result,
    kind: str,
) -> tuple[list[ClassifiedChange], int]:
    changes: list[ClassifiedChange] = []

    if before != after:
        for file_hunk in diff_result.files:
            if file_hunk.path == rel_path and file_hunk.diff_hunks:
                change_counter += 1
                changes.append(
                    ClassifiedChange(
                        change_id=f"CHG{change_counter:03d}",
                        change_type="modified",
                        category=kind,
                        file=rel_path,
                        line=0,
                        before=f"{len((before or '').splitlines())} lines",
                        after=f"{len((after or '').splitlines())} lines",
                    )
                )
                break

    return changes, change_counter
