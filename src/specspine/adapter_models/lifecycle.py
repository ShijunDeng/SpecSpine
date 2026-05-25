from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "NATIVE_STATUS_MEANINGS",
    "LOCAL_LIFECYCLE_COMMANDS",
    "AdapterLifecycleMapping",
    "AdapterLifecycleAdapter",
    "AdapterLifecycleReport",
    "ADAPTER_LIFECYCLE_MAPPINGS",
]

NATIVE_STATUS_MEANINGS: dict[str, str] = {
    "proposed": "Intent and scope are captured, but the implementation plan is not committed yet.",
    "planned": "Architecture, task shape, and quality gates are ready for implementation.",
    "in-progress": "Implementation is underway against the accepted local plan.",
    "implemented": "Code and documentation are written and waiting for validation evidence.",
    "validated": "Local checks, review evidence, and release readiness are complete.",
    "archived": "The work is complete or closed and retained as historical context.",
}

LOCAL_LIFECYCLE_COMMANDS: dict[str, tuple[str, ...]] = {
    "proposed": (
        'specspine feature new <slug> . --title "..." --why "..."',
        "specspine feature status <slug> . --set planned --enforce-transition --json",
    ),
    "planned": (
        "specspine feature handoff <slug> . --json",
        "specspine feature tasks <slug> . --json",
    ),
    "in-progress": (
        "specspine feature tasks <slug> . --json",
        "specspine feature trace <slug> . --json",
    ),
    "implemented": (
        "specspine feature tests <slug> . --json",
        "specspine feature ready <slug> . --json",
    ),
    "validated": (
        "specspine feature pr <slug> . --json",
        "specspine validate . --fusion --features",
    ),
    "archived": (
        "specspine feature status <slug> . --set archived --enforce-transition --json",
        "specspine status . --json --validate",
    ),
}


@dataclass(frozen=True)
class AdapterLifecycleMapping:
    id: str
    status: str
    specspine_meaning: str
    upstream_phase: str
    upstream_artifacts: tuple[str, ...]
    agent_focus: str
    local_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "agent_focus": self.agent_focus,
            "id": self.id,
            "local_commands": list(self.local_commands),
            "specspine_meaning": self.specspine_meaning,
            "status": self.status,
            "upstream_artifacts": list(self.upstream_artifacts),
            "upstream_phase": self.upstream_phase,
        }


@dataclass(frozen=True)
class AdapterLifecycleAdapter:
    key: str
    display_name: str
    enabled: bool
    config: str
    config_exists: bool
    upstream_url: str
    mappings: tuple[AdapterLifecycleMapping, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "config": self.config,
            "config_exists": self.config_exists,
            "display_name": self.display_name,
            "enabled": self.enabled,
            "mappings": [mapping.as_dict() for mapping in self.mappings],
            "upstream_url": self.upstream_url,
        }


@dataclass(frozen=True)
class AdapterLifecycleReport:
    root: Path
    native_statuses: tuple[str, ...]
    adapters: dict[str, AdapterLifecycleAdapter]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, int]:
        return {
            "adapters_total": len(self.adapters),
            "enabled_adapters": sum(1 for adapter in self.adapters.values() if adapter.enabled),
            "mappings_total": sum(len(adapter.mappings) for adapter in self.adapters.values()),
            "statuses_total": len(self.native_statuses),
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "adapters": {
                key: adapter.as_dict()
                for key, adapter in self.adapters.items()
            },
            "native_statuses": list(self.native_statuses),
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "summary": self.summary,
        }


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
            "Check that planned tasks landed before final quality validation.",
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
