from __future__ import annotations

from .feature_bundle import FeatureMetadata, FeatureSyncPlanCommand


def _recommended_sync_plan_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature sync-plan {slug} . --json",
        f"specspine feature issue {slug} . --json",
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature pr {slug} . --json",
        f"specspine feature ready {slug} . --json",
        "specspine adapters lifecycle . --json",
        "specspine validate . --fusion --features",
    )


def _sync_command(
    *,
    command_id: str,
    kind: str,
    description: str,
    argv: tuple[str, ...],
    body_source: str,
    body: str,
) -> FeatureSyncPlanCommand:
    return FeatureSyncPlanCommand(
        id=command_id,
        kind=kind,
        description=description,
        argv=argv,
        body_source=body_source,
        body=body,
    )


def _sync_plan_notes(metadata: FeatureMetadata) -> tuple[str, ...]:
    notes = [
        (
            "SpecSpine generated this as a local review plan only; it did not "
            "execute gh, call GitHub APIs, read tokens, or access the network."
        ),
        (
            "Every command would create remote GitHub resources if a human runs "
            "it, so review the argv list, labels, and draft body first."
        ),
        (
            "A human must authenticate GitHub CLI before running these commands; "
            "adding issues or pull requests to Projects may require the gh "
            "project scope."
        ),
        (
            "Do not rely on gh pr create dry-run as an automatic safety mode; "
            "GitHub CLI documentation says dry-run may still push git changes."
        ),
        (
            f"Priority is represented as the compatible label "
            f"priority:{metadata.priority}; this plan does not call GitHub Issue "
            "Fields APIs."
        ),
        (
            "Milestone, target release, project, and effort are local SpecSpine "
            "draft context in this plan; SpecSpine does not call GitHub Issue "
            "Fields or Projects APIs."
        ),
    ]
    if metadata.owner == "unassigned":
        notes.append(
            "Owner is unassigned; local owner metadata is not automatically "
            "mapped to --assignee."
        )
    else:
        notes.append(
            f"Owner '{metadata.owner}' is local SpecSpine metadata and is not "
            "automatically mapped to --assignee."
        )
    return tuple(notes)


__all__ = [
    "_recommended_sync_plan_commands",
    "_sync_command",
    "_sync_plan_notes",
]
