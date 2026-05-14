from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from .features import FEATURE_STATUSES


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


def _clean_config_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _parse_fusion_upstreams(content: str) -> dict[str, dict[str, Any]]:
    upstreams: dict[str, dict[str, Any]] = {}
    in_upstreams = False
    current_key: str | None = None

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            in_upstreams = stripped == "upstreams:"
            current_key = None
            continue

        if not in_upstreams:
            continue

        if indent == 2 and stripped.endswith(":"):
            current_key = stripped[:-1]
            upstreams.setdefault(current_key, {})
            continue

        if indent == 4 and current_key and ":" in stripped:
            key, value = stripped.split(":", 1)
            upstreams[current_key][key.strip()] = _clean_config_scalar(value)

    return upstreams


def _read_fusion_upstreams(root: Path) -> dict[str, dict[str, Any]]:
    fusion_path = root / ".specspine" / "fusion.yaml"
    if not fusion_path.exists():
        return {}

    try:
        return _parse_fusion_upstreams(fusion_path.read_text(encoding="utf-8"))
    except OSError:
        return {}


def _adapter_lifecycle_recommended_commands() -> tuple[str, ...]:
    return (
        "specspine status . --json --validate",
        "specspine adapters doctor",
        "specspine validate . --fusion --features",
    )


def build_adapter_lifecycle_report(root: Path) -> AdapterLifecycleReport:
    resolved_root = root.expanduser().resolve()
    fusion_upstreams = _read_fusion_upstreams(resolved_root)
    adapters: dict[str, AdapterLifecycleAdapter] = {}

    for key, spec in ADAPTER_SPECS.items():
        fusion_config = fusion_upstreams.get(key, {})
        adapter_path = fusion_config.get("adapter")
        if not isinstance(adapter_path, str) or not adapter_path:
            adapter_path = f".specspine/adapters/{key}.md"

        enabled = fusion_config.get("enabled", False)
        if not isinstance(enabled, bool):
            enabled = False

        adapters[key] = AdapterLifecycleAdapter(
            key=key,
            display_name=spec.display_name,
            enabled=enabled,
            config=adapter_path,
            config_exists=(resolved_root / adapter_path).exists(),
            upstream_url=spec.upstream_url,
            mappings=ADAPTER_LIFECYCLE_MAPPINGS[key],
        )

    return AdapterLifecycleReport(
        root=resolved_root,
        native_statuses=FEATURE_STATUSES,
        adapters=adapters,
        recommended_commands=_adapter_lifecycle_recommended_commands(),
    )


def render_adapter_lifecycle_json(report: AdapterLifecycleReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_adapter_lifecycle_text(report: AdapterLifecycleReport) -> str:
    summary = report.summary
    lines = [
        f"Adapter lifecycle mappings: {report.root}",
        (
            "Summary: "
            f"adapters={summary['adapters_total']} "
            f"enabled={summary['enabled_adapters']} "
            f"statuses={summary['statuses_total']} "
            f"mappings={summary['mappings_total']}"
        ),
    ]

    for key in ADAPTER_SPECS:
        adapter = report.adapters[key]
        enabled = "yes" if adapter.enabled else "no"
        config_exists = "yes" if adapter.config_exists else "no"
        lines.extend(
            [
                "",
                f"{adapter.display_name} ({key})",
                f"Enabled: {enabled}",
                f"Config: {adapter.config} (exists: {config_exists})",
                f"Upstream: {adapter.upstream_url}",
                "Mappings:",
            ]
        )
        for mapping in adapter.mappings:
            lines.append(
                f"- {mapping.id} {mapping.status} -> {mapping.upstream_phase}"
            )
            lines.append(f"  focus: {mapping.agent_focus}")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"


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


def get_agent_profile(agent: str) -> AgentProfile:
    try:
        return AGENT_PROFILES[agent]
    except KeyError as exc:
        supported = ", ".join(sorted(AGENT_PROFILES))
        raise ValueError(f"Unsupported agent {agent!r}. Supported agents: {supported}") from exc


def default_runner(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _clean_version(output: str) -> str | None:
    value = output.strip()
    if not value:
        return None
    return value.splitlines()[0].strip()


def _candidate_superpowers_paths() -> Iterable[Path]:
    env_path = os.environ.get("SPECSPINE_SUPERPOWERS_PATH")
    if env_path:
        yield Path(env_path)

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    yield codex_home / "plugins" / "superpowers"
    yield codex_home / ".tmp" / "plugins" / "plugins" / "superpowers"
    yield Path.home() / ".claude" / "plugins" / "superpowers"


def find_superpowers_install() -> Path | None:
    for path in _candidate_superpowers_paths():
        if (path / "skills").exists() or (path / ".codex-plugin" / "plugin.json").exists():
            return path
    return None


def read_superpowers_version(path: Path) -> str | None:
    plugin_json = path / ".codex-plugin" / "plugin.json"
    if not plugin_json.exists():
        return None

    try:
        payload = json.loads(plugin_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    version = payload.get("version")
    if isinstance(version, str):
        return version
    return None


def probe_adapter(
    key: str,
    *,
    runner: CommandRunner = default_runner,
) -> AdapterStatus:
    spec = ADAPTER_SPECS[key]

    if spec.key == "superpowers":
        install_path = find_superpowers_install()
        if install_path is None:
            return AdapterStatus(
                key=spec.key,
                display_name=spec.display_name,
                available=False,
                detail="Plugin install was not found in known local agent paths.",
                version=None,
                command=None,
                install_hint=spec.install_hint,
                upstream_url=spec.upstream_url,
            )

        return AdapterStatus(
            key=spec.key,
            display_name=spec.display_name,
            available=True,
            detail=f"Found plugin at {install_path}",
            version=read_superpowers_version(install_path),
            command=None,
            install_hint=spec.install_hint,
            upstream_url=spec.upstream_url,
        )

    if spec.command is None:
        return AdapterStatus(
            key=spec.key,
            display_name=spec.display_name,
            available=False,
            detail="No command-based probe is defined.",
            version=None,
            command=None,
            install_hint=spec.install_hint,
            upstream_url=spec.upstream_url,
        )

    command_path = shutil.which(spec.command)
    if command_path is None:
        return AdapterStatus(
            key=spec.key,
            display_name=spec.display_name,
            available=False,
            detail=f"{spec.command!r} was not found on PATH.",
            version=None,
            command=spec.command,
            install_hint=spec.install_hint,
            upstream_url=spec.upstream_url,
        )

    result = runner((spec.command, *spec.version_args), Path.cwd())
    version = _clean_version(result.stdout) or _clean_version(result.stderr)

    return AdapterStatus(
        key=spec.key,
        display_name=spec.display_name,
        available=result.returncode == 0,
        detail=f"{spec.command!r} resolved to {command_path}",
        version=version,
        command=spec.command,
        install_hint=spec.install_hint,
        upstream_url=spec.upstream_url,
    )


def probe_adapters(
    keys: Iterable[str] = ADAPTER_SPECS,
    *,
    runner: CommandRunner = default_runner,
) -> list[AdapterStatus]:
    return [probe_adapter(key, runner=runner) for key in keys]


def build_upstream_init_commands(
    *,
    agent: str,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
    force: bool = False,
) -> list[UpstreamCommand]:
    profile = get_agent_profile(agent)
    commands: list[UpstreamCommand] = []

    if include_openspec:
        args = ["openspec", "init", ".", "--tools", profile.openspec_tool]
        if force:
            args.append("--force")
        commands.append(
            UpstreamCommand(
                key="openspec",
                description="Initialize OpenSpec using its own CLI.",
                args=tuple(args),
            )
        )

    if include_speckit:
        commands.append(
            UpstreamCommand(
                key="speckit",
                description="Initialize Spec Kit using its own Specify CLI.",
                args=("specify", "init", ".", "--integration", profile.speckit_integration),
            )
        )

    if include_superpowers:
        commands.append(
            UpstreamCommand(
                key="superpowers",
                description="Verify that the Superpowers agent plugin/extension is installed.",
                args=(),
            )
        )

    return commands


def run_upstream_initializers(
    root: Path,
    commands: Iterable[UpstreamCommand],
    *,
    runner: CommandRunner = default_runner,
) -> list[UpstreamCommandResult]:
    results: list[UpstreamCommandResult] = []
    root = root.expanduser().resolve()

    for command in commands:
        if not command.args:
            status = probe_adapter(command.key)
            results.append(
                UpstreamCommandResult(
                    key=command.key,
                    command=command.description,
                    returncode=0 if status.available else 1,
                    stdout=status.detail,
                    stderr="" if status.available else status.install_hint,
                )
            )
            continue

        executable = command.args[0]
        if shutil.which(executable) is None:
            spec = ADAPTER_SPECS[command.key]
            results.append(
                UpstreamCommandResult(
                    key=command.key,
                    command=command.display(),
                    returncode=127,
                    stdout="",
                    stderr=f"{executable!r} is not installed. {spec.install_hint}",
                )
            )
            continue

        result = runner(command.args, root)
        results.append(
            UpstreamCommandResult(
                key=command.key,
                command=command.display(),
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        )

    return results
