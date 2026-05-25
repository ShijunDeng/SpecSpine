from __future__ import annotations

from .lifecycle_constants import NATIVE_STATUS_MEANINGS, LOCAL_LIFECYCLE_COMMANDS
from .lifecycle_models import AdapterLifecycleMapping

__all__ = [
    "_lifecycle_mapping",
    "ADAPTER_LIFECYCLE_MAPPINGS",
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


ADAPTER_LIFECYCLE_MAPPINGS: dict[str, tuple[AdapterLifecycleMapping, ...]] = {
    "openspec": (
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
    ),
    "speckit": (
        _lifecycle_mapping(
            "speckit",
            "proposed",
            "Spec phase",
            ("specs/<feature>/spec.md", ".specify/"),
            "Capture user value, scenarios, constraints, and acceptance criteria.",
        ),
        _lifecycle_mapping(
            "speckit",
            "planned",
            "Plan phase",
            (
                "specs/<feature>/plan.md",
                "specs/<feature>/research.md",
                "specs/<feature>/data-model.md",
                "specs/<feature>/contracts/",
            ),
            "Turn the spec into architecture, research, contracts, and implementation shape.",
        ),
        _lifecycle_mapping(
            "speckit",
            "in-progress",
            "Tasks and implement phase",
            ("specs/<feature>/tasks.md", "implementation files"),
            "Drive implementation from the task list while preserving spec traceability.",
        ),
        _lifecycle_mapping(
            "speckit",
            "implemented",
            "Implementation complete against tasks",
            ("specs/<feature>/tasks.md", "source changes", "documentation updates"),
            "Check that planned tasks landed before final quality validations.",
        ),
        _lifecycle_mapping(
            "speckit",
            "validated",
            "Checklist, analyze, and governance checks passed",
            ("specs/<feature>/checklists/", "constitution checks", "test evidence"),
            "Use checklist and analysis evidence to confirm the implementation matches the spec.",
        ),
        _lifecycle_mapping(
            "speckit",
            "archived",
            "Feature folder retained as release history",
            ("specs/<feature>/", "release notes"),
            "Keep completed spec, plan, tasks, and evidence available for future agents.",
        ),
    ),
    "superpowers": (
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
    ),
}
