from __future__ import annotations

from .evolution_classification import ClassifiedChange
from .features import FEATURE_FILE_PATHS
from .evolution_impact_models import ImpactEntry, RemediationAction

__all__ = [
    "_generate_removed_ac_remediation_actions",
]


def _generate_removed_ac_remediation_actions(
    change: ClassifiedChange,
    relevant_impacts: list[ImpactEntry],
    action_counter: int,
) -> tuple[list[RemediationAction], int]:
    actions: list[RemediationAction] = []

    ac_id = change.before or "unknown"
    action_counter += 1
    actions.append(
        RemediationAction(
            action_id=f"ACT{action_counter:03d}",
            description=f"Update downstream features referencing removed AC {ac_id}",
            priority=1,
            target_file=change.file,
        )
    )
    for impact in relevant_impacts:
        if impact.affected_type == "coverage":
            action_counter += 1
            actions.append(
                RemediationAction(
                    action_id=f"ACT{action_counter:03d}",
                    description=f"Remove coverage link {impact.affected_id} from quality file",
                    priority=2,
                    target_file=FEATURE_FILE_PATHS["quality"].format(slug=change.file.split("/")[-1].replace(".md", "")),
                )
            )
        elif impact.affected_type == "feature":
            action_counter += 1
            actions.append(
                RemediationAction(
                    action_id=f"ACT{action_counter:03d}",
                    description=f"Re-validate feature {impact.affected_id} that depends on removed AC",
                    priority=1,
                    target_file=FEATURE_FILE_PATHS["spec"].format(slug=impact.affected_id),
                )
            )

    return actions, action_counter
