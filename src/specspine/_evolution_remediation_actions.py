from __future__ import annotations

from .evolution_classification import ClassifiedChange
from .features import FEATURE_FILE_PATHS
from .evolution_impact_models import ImpactEntry, RemediationAction
from ._remediation_ac_actions import _generate_ac_remediation_actions
from ._remediation_task_actions import _generate_task_remediation_actions

__all__ = [
    "generate_remediation_plan",
]


def generate_remediation_plan(
    changes: list[ClassifiedChange],
    impacts: list[ImpactEntry],
) -> list[RemediationAction]:
    actions: list[RemediationAction] = []
    action_counter = 0

    impact_by_change: dict[str, list[ImpactEntry]] = {}
    for impact in impacts:
        if impact.severity == "info":
            continue
        if impact.change_id not in impact_by_change:
            impact_by_change[impact.change_id] = []
        impact_by_change[impact.change_id].append(impact)

    for change in changes:
        relevant_impacts = impact_by_change.get(change.change_id, [])
        if not relevant_impacts:
            continue

        if change.category == "ac":
            ac_actions, action_counter = _generate_ac_remediation_actions(
                change, relevant_impacts, action_counter,
            )
            actions.extend(ac_actions)
        elif change.category == "task":
            task_actions, action_counter = _generate_task_remediation_actions(
                change, action_counter,
            )
            actions.extend(task_actions)

    actions.sort(key=lambda a: a.priority)
    return actions
