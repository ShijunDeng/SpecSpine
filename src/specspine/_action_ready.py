from __future__ import annotations

from ._action_utils import _append_unique

__all__ = [
    "_collect_ready_actions",
]


def _collect_ready_actions(
    actions: list[str],
    ready: bool,
) -> None:
    if ready:
        _append_unique(
            actions,
            "Review, merge, or archive the ready feature bundle.",
        )
