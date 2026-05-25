from __future__ import annotations

from .feature_bundle import (
    FeatureReadyCheck,
    FeatureTask,
)
from ._action_utils import _append_unique

__all__ = [
    "_collect_task_actions",
    "_collect_blocking_actions",
]


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
