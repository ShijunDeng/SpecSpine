from __future__ import annotations

from ..lifecycle_constants import NATIVE_STATUS_MEANINGS, LOCAL_LIFECYCLE_COMMANDS
from ..lifecycle_models import AdapterLifecycleMapping

__all__ = [
    "SUPERPOWERS_LIFECYCLE_MAPPINGS",
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


SUPERPOWERS_LIFECYCLE_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
    _lifecycle_mapping(
        "superpowers",
        "proposed",
        "Brainstorming and requirements clarification",
        ("brainstorming notes", "requirements conversation"),
        "Challenge unclear intent and identify missing context before planning.",
    ),
    _lifecycle_mapping(
        "superpowers",
        "planned",
        "Writing plans",
        ("implementation plan", "review checklist"),
        "Produce an executable plan with explicit risks, tasks, and validation steps.",
    ),
    _lifecycle_mapping(
        "superpowers",
        "in-progress",
        "TDD and subagent-driven development",
        ("tests", "task progress", "subagent handoffs"),
        "Keep tests, implementation, and subagent feedback aligned with the plan.",
    ),
    _lifecycle_mapping(
        "superpowers",
        "implemented",
        "Development branch ready for review",
        ("code changes", "test results", "review request"),
        "Request review against the original plan and surface unresolved risks.",
    ),
    _lifecycle_mapping(
        "superpowers",
        "validated",
        "Verification before completion",
        ("verification results", "code review findings", "release readiness notes"),
        "Confirm tests, review, and completion evidence before handing off.",
    ),
    _lifecycle_mapping(
        "superpowers",
        "archived",
        "Finishing a development branch",
        ("completion notes", "merged or closed branch record"),
        "Preserve the final evidence and any follow-up notes for future work.",
    ),
)
