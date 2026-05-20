from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "ADAPTER_HANDOFF_SAFETY_FLAGS",
    "ADAPTER_LIFECYCLE_MAPPINGS",
    "ADAPTER_SPECS",
    "AGENT_PROFILES",
    "AdapterFeatureHandoffEntry",
    "AdapterFeatureHandoffReport",
    "AdapterHandoffArtifactExistsError",
    "AdapterHandoffArtifacts",
    "AdapterHandoffStep",
    "AdapterLifecycleAdapter",
    "AdapterLifecycleMapping",
    "AdapterLifecycleReport",
    "AdapterSpec",
    "AdapterStatus",
    "AgentProfile",
    "CommandRunner",
    "LOCAL_LIFECYCLE_COMMANDS",
    "NATIVE_STATUS_MEANINGS",
    "UpstreamCommand",
    "UpstreamCommandResult",
]

import subprocess
from typing import Callable, Sequence

CommandRunner = Callable[[Sequence[str], Path], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class AgentProfile:
    key: str
    openspec_tool: str
    speckit_integration: str
    superpowers_hint: str


AGENT_PROFILES: dict[str, AgentProfile] = {
    "codex": AgentProfile(
        key="codex",
        openspec_tool="codex",
        speckit_integration="codex",
        superpowers_hint="Install the Superpowers plugin from the Codex plugin marketplace.",
    ),
    "claude": AgentProfile(
        key="claude",
        openspec_tool="claude",
        speckit_integration="claude",
        superpowers_hint="Install Superpowers with /plugin install superpowers@claude-plugins-official.",
    ),
    "copilot": AgentProfile(
        key="copilot",
        openspec_tool="github-copilot",
        speckit_integration="copilot",
        superpowers_hint="Install Superpowers from the GitHub Copilot CLI plugin marketplace.",
    ),
    "cursor": AgentProfile(
        key="cursor",
        openspec_tool="cursor",
        speckit_integration="cursor-agent",
        superpowers_hint="Install Superpowers from the Cursor plugin marketplace.",
    ),
    "gemini": AgentProfile(
        key="gemini",
        openspec_tool="gemini",
        speckit_integration="gemini",
        superpowers_hint="Install Superpowers with gemini extensions install https://github.com/obra/superpowers.",
    ),
    "opencode": AgentProfile(
        key="opencode",
        openspec_tool="opencode",
        speckit_integration="opencode",
        superpowers_hint="Follow the OpenCode install instructions from the Superpowers repository.",
    ),
    "windsurf": AgentProfile(
        key="windsurf",
        openspec_tool="windsurf",
        speckit_integration="windsurf",
        superpowers_hint="Install Superpowers through Windsurf-compatible agent plugin support.",
    ),
}


@dataclass(frozen=True)
class AdapterSpec:
    key: str
    display_name: str
    role: str
    upstream_url: str
    license_name: str
    command: str | None
    version_args: tuple[str, ...]
    install_hint: str


ADAPTER_SPECS: dict[str, AdapterSpec] = {
    "openspec": AdapterSpec(
        key="openspec",
        display_name="OpenSpec",
        role="change proposals, living spec deltas, and artifact-guided spec lifecycle",
        upstream_url="https://github.com/Fission-AI/OpenSpec",
        license_name="MIT",
        command="openspec",
        version_args=("--version",),
        install_hint="npm install -g @fission-ai/openspec@latest",
    ),
    "speckit": AdapterSpec(
        key="speckit",
        display_name="Spec Kit",
        role="intent-first specification, planning, task breakdown, and agent integration files",
        upstream_url="https://github.com/github/spec-kit",
        license_name="MIT",
        command="specify",
        version_args=("version",),
        install_hint="uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z",
    ),
    "superpowers": AdapterSpec(
        key="superpowers",
        display_name="Superpowers",
        role="software engineering discipline: brainstorming, planning, TDD, subagent execution, and review",
        upstream_url="https://github.com/obra/superpowers",
        license_name="MIT",
        command=None,
        version_args=(),
        install_hint="Install the Superpowers plugin/extension for your AI coding agent.",
    ),
}


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


@dataclass(frozen=True)
class AdapterHandoffStep:
    id: str
    kind: str
    description: str
    argv: tuple[str, ...] = ()
    instruction: str = ""
    creates_remote: bool = False
    requires_network: bool = False
    requires_token: bool = False
    safe_to_auto_run: bool = False
    executed: bool = False

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "creates_remote": self.creates_remote,
            "description": self.description,
            "executed": self.executed,
            "id": self.id,
            "kind": self.kind,
            "requires_network": self.requires_network,
            "requires_token": self.requires_token,
            "safe_to_auto_run": self.safe_to_auto_run,
        }
        if self.argv:
            payload["argv"] = list(self.argv)
        if self.instruction:
            payload["instruction"] = self.instruction
        return payload


@dataclass(frozen=True)
class AdapterFeatureHandoffEntry:
    key: str
    display_name: str
    enabled: bool
    config: str
    config_exists: bool
    upstream_url: str
    integration_surface: str
    native_status: str
    upstream_phase: str
    upstream_artifacts: tuple[str, ...]
    agent_focus: str
    local_commands: tuple[str, ...]
    recommended_upstream_steps: tuple[AdapterHandoffStep, ...]
    notes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "agent_focus": self.agent_focus,
            "config": self.config,
            "config_exists": self.config_exists,
            "display_name": self.display_name,
            "enabled": self.enabled,
            "integration_surface": self.integration_surface,
            "key": self.key,
            "local_commands": list(self.local_commands),
            "native_status": self.native_status,
            "notes": list(self.notes),
            "recommended_upstream_steps": [
                step.as_dict() for step in self.recommended_upstream_steps
            ],
            "upstream_artifacts": list(self.upstream_artifacts),
            "upstream_phase": self.upstream_phase,
            "upstream_url": self.upstream_url,
        }


@dataclass(frozen=True)
class AdapterFeatureHandoffReport:
    root: Path
    feature_id: str
    status: str
    ready: bool
    sources: dict[str, dict[str, object]]
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple[Any, ...]
    feature_summary: dict[str, object]
    adapters: dict[str, AdapterFeatureHandoffEntry]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, object]:
        steps_total = sum(
            len(adapter.recommended_upstream_steps)
            for adapter in self.adapters.values()
        )
        return {
            "adapters": {
                "config_exists": sum(
                    1 for adapter in self.adapters.values() if adapter.config_exists
                ),
                "enabled": sum(
                    1 for adapter in self.adapters.values() if adapter.enabled
                ),
                "total": len(self.adapters),
            },
            "blocking_checks": {"total": len(self.blocking_checks)},
            "feature": dict(self.feature_summary),
            "gaps": {"total": len(self.gaps)},
            "steps": {"total": steps_total},
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "adapters": {
                key: adapter.as_dict()
                for key, adapter in self.adapters.items()
            },
            "blocking_checks": [
                check.as_dict() if hasattr(check, "as_dict") else dict(check)
                for check in self.blocking_checks
            ],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "missing_files": list(self.missing_files),
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "source_files": list(self.source_files),
            "sources": self.sources,
            "status": self.status,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class AdapterHandoffArtifactExistsError(FileExistsError):
    output_dir: Path
    existing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"Adapter handoff artifact files already exist in {self.output_dir}. "
            "Use --force to overwrite files written by this command."
        )


@dataclass(frozen=True)
class AdapterHandoffArtifacts:
    output_dir: Path
    manifest_path: Path
    combined_path: Path
    combined_json_path: Path
    adapter_paths: tuple[Path, ...]
    adapter_json_paths: tuple[Path, ...]
    written_paths: tuple[Path, ...]
    manifest: dict[str, object]


ADAPTER_HANDOFF_SAFETY_FLAGS: dict[str, bool] = {
    "creates_remote": False,
    "executed": False,
    "requires_network": False,
    "requires_token": False,
    "safe_to_auto_run": False,
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


@dataclass(frozen=True)
class AdapterStatus:
    key: str
    display_name: str
    available: bool
    detail: str
    version: str | None
    command: str | None
    install_hint: str
    upstream_url: str


@dataclass(frozen=True)
class UpstreamCommand:
    key: str
    description: str
    args: tuple[str, ...]

    def display(self) -> str:
        return " ".join(self.args)


@dataclass(frozen=True)
class UpstreamCommandResult:
    key: str
    command: str
    returncode: int
    stdout: str
    stderr: str
