from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

from ..adapter_models import ADAPTER_SPECS, AdapterStatus, CommandRunner
from ._probe_utils import _clean_version, default_runner
from ._probe_superpowers import find_superpowers_install, read_superpowers_version

__all__ = [
    "probe_adapter",
    "probe_adapters",
]


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
