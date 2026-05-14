from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence


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
