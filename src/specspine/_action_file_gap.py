from __future__ import annotations

from ._action_utils import _append_unique

__all__ = [
    "_collect_missing_file_actions",
    "_collect_gap_actions",
]


def _collect_missing_file_actions(
    actions: list[str],
    missing_files: tuple[str, ...],
) -> None:
    if missing_files:
        _append_unique(
            actions,
            "Add missing peer file(s): " + ", ".join(missing_files),
        )


def _collect_gap_actions(
    actions: list[str],
    gaps: tuple[dict[str, str], ...],
) -> None:
    section_gap_ids = tuple(
        gap["id"] for gap in gaps if gap["id"] != "missing_file"
    )
    if section_gap_ids:
        _append_unique(
            actions,
            "Fill missing trace section(s): " + ", ".join(section_gap_ids),
        )
