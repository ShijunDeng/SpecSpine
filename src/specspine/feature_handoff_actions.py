from __future__ import annotations

from .feature_bundle import (
    FeatureReadyCheck,
    FeatureTask,
)
from ._action_utils import _append_unique
from ._action_builder import (
    _collect_missing_file_actions,
    _collect_gap_actions,
    _collect_task_actions,
    _collect_blocking_actions,
    _collect_ready_actions,
)

__all__ = [
    "_append_unique",
    "_handoff_next_actions",
]


def _handoff_next_actions(
    *,
    slug: str,
    has_native_files: bool,
    missing_files: tuple[str, ...],
    gaps: tuple[dict[str, str], ...],
    tasks: tuple[FeatureTask, ...],
    blocking_checks: tuple[FeatureReadyCheck, ...],
    ready: bool,
) -> tuple[str, ...]:
    actions: list[str] = []

    if not has_native_files:
        _append_unique(
            actions,
            (
                "Create or restore the native feature bundle: "
                f"specspine feature new {slug} . --title \"...\" --why \"...\""
            ),
        )
        return tuple(actions)

    _collect_missing_file_actions(actions, missing_files)
    _collect_gap_actions(actions, gaps)
    _collect_task_actions(actions, tasks)
    _collect_blocking_actions(actions, blocking_checks)
    _collect_ready_actions(actions, ready)

    return tuple(actions)
