from __future__ import annotations

from .adapter_upstream_init import build_upstream_init_commands, run_upstream_initializers
from .adapter_upstream_probe import (
    default_runner,
    find_superpowers_install,
    get_agent_profile,
    probe_adapter,
    probe_adapters,
    read_superpowers_version,
)

__all__ = [
    "build_upstream_init_commands",
    "default_runner",
    "find_superpowers_install",
    "get_agent_profile",
    "probe_adapter",
    "probe_adapters",
    "read_superpowers_version",
    "run_upstream_initializers",
]
