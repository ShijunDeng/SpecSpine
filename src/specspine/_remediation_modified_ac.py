from __future__ import annotations

from .evolution_classification import ClassifiedChange
from .features import FEATURE_FILE_PATHS
from .evolution_impact_models import ImpactEntry, RemediationAction

__all__ = [
    "_generate_modified_ac_remediation_actions",
]


def _generate_modified_ac_remediation_actions(
    change: ClassifiedChange,
    relevant_impacts: list[ImpactEntry],
    action_counter: int,
) -> tuple[list[RemediationAction], int]:
    actions: list[RemediationAction] = []

    ac_id = change.after or change.before or "unknown"
    for impact in relevant_impacts:
        if impact.affected_type == "feature":
            action_counter += 1
            actions.append(
                RemediationAction(
                    action_id=f"ACT{action_counter:03d}",
                    description=f"Re-validate feature {impact.affected_id} for modified AC {ac_id}",
                    priority=2,
                    target_file=FEATURE_FILE_PATHS["quality"].format(slug=impact.affected_id),
                )
            )

    return actions, action_counter
