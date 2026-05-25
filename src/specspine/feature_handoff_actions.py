from __future__ import annotations

from .feature_bundle import (
    FeatureReadyCheck,
    FeatureTask,
)

__all__ = [
    "_append_unique",
    "_handoff_next_actions",
]


def _append_unique(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)


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

    if missing_files:
        _append_unique(
            actions,
            "Add missing peer file(s): " + ", ".join(missing_files),
        )

    section_gap_ids = tuple(
        gap["id"] for gap in gaps if gap["id"] != "missing_file"
    )
    if section_gap_ids:
        _append_unique(
            actions,
            "Fill missing trace section(s): " + ", ".join(section_gap_ids),
        )

    open_task_ids = tuple(task.id for task in tasks if not task.done)
    if open_task_ids:
        _append_unique(
            actions,
            "Complete open task(s): " + ", ".join(open_task_ids),
        )

    blocking_ids = tuple(check.id for check in blocking_checks)
    if blocking_ids:
        _append_unique(
            actions,
            "Resolve blocking readiness check(s): " + ", ".join(blocking_ids),
        )

    if ready:
        _append_unique(
            actions,
            "Review, merge, or archive the ready feature bundle.",
        )

    return tuple(actions)
