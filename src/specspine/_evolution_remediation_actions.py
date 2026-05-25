from __future__ import annotations

from .evolution_classification import ClassifiedChange
from .features import FEATURE_FILE_PATHS
from .evolution_impact_models import ImpactEntry, RemediationAction

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

        if change.change_type == "removed" and change.category == "ac":
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

        elif change.change_type == "modified" and change.category == "ac":
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

        elif change.change_type == "removed" and change.category == "task":
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

    actions.sort(key=lambda a: a.priority)
    return actions
