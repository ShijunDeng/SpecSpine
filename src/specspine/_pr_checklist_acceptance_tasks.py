from __future__ import annotations

from .feature_bundle import (
    FeatureTask,
    FeatureTraceChecklistItem,
)
from .feature_drafts_pr_renderers import (
    _render_pr_checklist_items,
)

__all__ = [
    "_render_pr_acceptance_criteria_section",
    "_render_pr_tasks_section",
]


def _render_pr_acceptance_criteria_section(
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
) -> list[str]:
    lines: list[str] = []
    lines.extend(["## Acceptance Criteria", ""])
    lines.extend(
        _render_pr_checklist_items(
            acceptance_criteria,
            empty_text="Add acceptance criteria checklist items before review.",
        )
    )
    return lines


def _render_pr_tasks_section(
    tasks: tuple[FeatureTask, ...],
) -> list[str]:
    lines: list[str] = []
    lines.extend(["", "## Tasks", ""])
    lines.extend(
        _render_pr_checklist_items(
            tasks,
            empty_text="Add execution task checklist items before review.",
        )
    )
    return lines
