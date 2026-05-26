from __future__ import annotations

from .feature_bundle import (
    FeatureReadyCheck,
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
)
from ._pr_checklist_acceptance_tasks import (
    _render_pr_acceptance_criteria_section,
    _render_pr_tasks_section,
)
from ._pr_checklist_test_plan import _render_pr_test_plan_section
from ._pr_checklist_readiness import (
    _render_pr_readiness_checks_section,
    _render_pr_release_readiness_section,
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

    lines.extend(_render_pr_acceptance_criteria_section(acceptance_criteria))
    lines.extend(_render_pr_tasks_section(tasks))
    lines.extend(_render_pr_test_plan_section(test_plan))
    lines.extend(_render_pr_release_readiness_section(release_readiness))
    lines.extend(_render_pr_readiness_checks_section(readiness_checks))

    return lines
