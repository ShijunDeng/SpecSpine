from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Sequence

from .adapter_models import (
    ADAPTER_SPECS,
    AGENT_PROFILES,
    AdapterStatus,
    AgentProfile,
    CommandRunner,
)


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
        import json
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


__all__ = [
    "default_runner",
    "find_superpowers_install",
    "get_agent_profile",
    "probe_adapter",
    "probe_adapters",
    "read_superpowers_version",
]
