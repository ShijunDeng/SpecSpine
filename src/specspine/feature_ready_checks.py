from __future__ import annotations

from .feature_bundle import (
    FeatureReadyCheck,
    FeatureTraceChecklistItem,
    FeatureTask,
)

__all__ = [
    "FeatureReadyCheck",
    "_ready_check",
    "_checklist_ready_message",
]


def _ready_check(check_id: str, passed: bool, message: str) -> FeatureReadyCheck:
    return FeatureReadyCheck(
        id=check_id,
        status="pass" if passed else "fail",
        message=message,
    )


def _checklist_ready_message(
    *,
    label: str,
    items: tuple[FeatureTraceChecklistItem, ...] | tuple[FeatureTask, ...],
) -> tuple[bool, str]:
    total = len(items)
    done = sum(1 for item in items if item.done)
    open_count = total - done
    if total == 0:
        return False, f"No {label} checklist items found."
    if open_count:
        return False, f"{label.title()} incomplete: {open_count} open of {total}."
    return True, f"{label.title()} complete: {done} of {total} done."
