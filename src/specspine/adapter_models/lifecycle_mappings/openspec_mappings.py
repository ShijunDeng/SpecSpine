from __future__ import annotations

from ..lifecycle_constants import NATIVE_STATUS_MEANINGS, LOCAL_LIFECYCLE_COMMANDS
from ..lifecycle_models import AdapterLifecycleMapping

__all__ = [
    "OPENSCPEC_LIFECYCLE_MAPPINGS",
]


def _lifecycle_mapping(
    adapter: str,
    status: str,
    upstream_phase: str,
    upstream_artifacts: tuple[str, ...],
    agent_focus: str,
) -> AdapterLifecycleMapping:
    return AdapterLifecycleMapping(
        id=f"{adapter}:{status}",
        status=status,
        specspine_meaning=NATIVE_STATUS_MEANINGS[status],
        upstream_phase=upstream_phase,
        upstream_artifacts=upstream_artifacts,
        agent_focus=agent_focus,
        local_commands=LOCAL_LIFECYCLE_COMMANDS[status],
    )


OPENSCPEC_LIFECYCLE_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
    _lifecycle_mapping(
        "openspec",
        "proposed",
        "Change proposal drafted",
        ("openspec/changes/<change-id>/proposal.md", "openspec/changes/<change-id>/specs/"),
        "Clarify why the change exists and what capability delta it proposes.",
    ),
    _lifecycle_mapping(
        "openspec",
        "planned",
        "Design and task plan ready",
        (
            "openspec/changes/<change-id>/proposal.md",
            "openspec/changes/<change-id>/design.md",
            "openspec/changes/<change-id>/tasks.md",
            "openspec/changes/<change-id>/specs/",
        ),
        "Review design tradeoffs, spec deltas, and ordered tasks before implementation.",
    ),
    _lifecycle_mapping(
        "openspec",
        "in-progress",
        "Change implementation active",
        ("openspec/changes/<change-id>/tasks.md", "openspec/changes/<change-id>/specs/"),
        "Keep implementation work tied to the approved change tasks and spec deltas.",
    ),
    _lifecycle_mapping(
        "openspec",
        "implemented",
        "Change artifacts complete before validation",
        ("openspec/changes/<change-id>/tasks.md", "openspec/changes/<change-id>/design.md"),
        "Confirm tasks and implementation evidence are complete before validation.",
    ),
    _lifecycle_mapping(
        "openspec",
        "validated",
        "OpenSpec validation and review passed",
        ("openspec validate --all", "openspec/changes/<change-id>/"),
        "Use validation findings to close drift between proposal, specs, and code.",
    ),
    _lifecycle_mapping(
        "openspec",
        "archived",
        "Change archived into living specs",
        ("openspec/specs/", "openspec/changes/archive/"),
        "Retain the accepted change history after the living specs are updated.",
    ),
)
