from __future__ import annotations

from .feature_bundle import (
    FeatureReadyCheck,
    FeatureTask,
)
from ._action_utils import _append_unique

__all__ = [
    "_collect_missing_file_actions",
    "_collect_gap_actions",
    "_collect_task_actions",
    "_collect_blocking_actions",
    "_collect_ready_actions",
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


def _collect_task_actions(
    actions: list[str],
    tasks: tuple[FeatureTask, ...],
) -> None:
    open_task_ids = tuple(task.id for task in tasks if not task.done)
    if open_task_ids:
        _append_unique(
            actions,
            "Complete open task(s): " + ", ".join(open_task_ids),
        )


def _collect_blocking_actions(
    actions: list[str],
    blocking_checks: tuple[FeatureReadyCheck, ...],
) -> None:
    blocking_ids = tuple(check.id for check in blocking_checks)
    if blocking_ids:
        _append_unique(
            actions,
            "Resolve blocking readiness check(s): " + ", ".join(blocking_ids),
        )


def _collect_ready_actions(
    actions: list[str],
    ready: bool,
) -> None:
    if ready:
        _append_unique(
            actions,
            "Review, merge, or archive the ready feature bundle.",
        )
