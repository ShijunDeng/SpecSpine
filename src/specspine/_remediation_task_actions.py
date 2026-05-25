from __future__ import annotations

from .evolution_classification import ClassifiedChange
from .features import FEATURE_FILE_PATHS
from .evolution_impact_models import ImpactEntry, RemediationAction

__all__ = [
    "_generate_task_remediation_actions",
]


def _generate_task_remediation_actions(
    change: ClassifiedChange,
    action_counter: int,
) -> tuple[list[RemediationAction], int]:
    actions: list[RemediationAction] = []

    if change.change_type == "removed" and change.category == "task":
        task_id = change.before or "unknown"
        action_counter += 1
        actions.append(
            RemediationAction(
                action_id=f"ACT{action_counter:03d}",
                description=f"Update execution file for removed task {task_id}",
                priority=1,
                target_file=FEATURE_FILE_PATHS["execution"].format(
                    slug=change.file.split("/")[-1].replace(".md", "")
                ),
            )
        )

    elif change.change_type == "added" and change.category == "task":
        task_id = change.after or "unknown"
        action_counter += 1
        actions.append(
            RemediationAction(
                action_id=f"ACT{action_counter:03d}",
                description=f"Add test coverage for new task {task_id}",
                priority=3,
                target_file=FEATURE_FILE_PATHS["quality"].format(
                    slug=change.file.split("/")[-1].replace(".md", "")
                ),
            )
        )

    return actions, action_counter
