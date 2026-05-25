from __future__ import annotations

from .feature_bundle import (
    FeatureReadyCheck,
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
)
from .feature_drafts_pr_renderers import (
    _render_pr_checklist_items,
    _render_pr_test_plan_items,
    _render_pr_ready_checks,
)

__all__ = [
    "_render_pr_checklist_sections",
]


def _render_pr_checklist_sections(
    *,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    tasks: tuple[FeatureTask, ...],
    test_plan: tuple[FeatureTraceTestPlanItem, ...],
    release_readiness: tuple[FeatureTraceChecklistItem, ...],
    readiness_checks: tuple[FeatureReadyCheck, ...],
) -> list[str]:
    lines: list[str] = []

    lines.extend(["## Acceptance Criteria", ""])
    lines.extend(
        _render_pr_checklist_items(
            acceptance_criteria,
            empty_text="Add acceptance criteria checklist items before review.",
        )
    )

    lines.extend(["", "## Tasks", ""])
    lines.extend(
        _render_pr_checklist_items(
            tasks,
            empty_text="Add execution task checklist items before review.",
        )
    )

    lines.extend(["", "## Test Plan", ""])
    lines.extend(
        _render_pr_test_plan_items(
            test_plan,
            empty_text="Add a concrete test plan before review.",
        )
    )

    lines.extend(["", "## Release Readiness", ""])
    lines.extend(
        _render_pr_checklist_items(
            release_readiness,
            empty_text="Add release readiness checklist items before review.",
        )
    )

    lines.extend(["", "## Readiness / Blocking Checks", ""])
    lines.extend(_render_pr_ready_checks(readiness_checks))

    return lines
