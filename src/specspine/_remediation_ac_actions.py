from __future__ import annotations

from ._remediation_modified_ac import _generate_modified_ac_remediation_actions
from ._remediation_removed_ac import _generate_removed_ac_remediation_actions
from .evolution_classification import ClassifiedChange
from .evolution_impact_models import ImpactEntry, RemediationAction

__all__ = [
    "_generate_ac_remediation_actions",
]


def _generate_ac_remediation_actions(
    change: ClassifiedChange,
    relevant_impacts: list[ImpactEntry],
    action_counter: int,
) -> tuple[list[RemediationAction], int]:
    actions: list[RemediationAction] = []

    if change.change_type == "removed" and change.category == "ac":
        removed_actions, action_counter = _generate_removed_ac_remediation_actions(
            change, relevant_impacts, action_counter
        )
        actions.extend(removed_actions)

    elif change.change_type == "modified" and change.category == "ac":
        modified_actions, action_counter = _generate_modified_ac_remediation_actions(
            change, relevant_impacts, action_counter
        )
        actions.extend(modified_actions)

    return actions, action_counter
