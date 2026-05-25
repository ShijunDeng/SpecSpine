from __future__ import annotations

from ..lifecycle_constants import NATIVE_STATUS_MEANINGS, LOCAL_LIFECYCLE_COMMANDS
from ..lifecycle_models import AdapterLifecycleMapping

__all__ = [
    "SPECKIT_LIFECYCLE_MAPPINGS",
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


SPECKIT_LIFECYCLE_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
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
)
