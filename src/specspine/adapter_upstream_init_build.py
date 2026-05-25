from __future__ import annotations

from .adapter_upstream_probe import get_agent_profile
from .adapter_models import UpstreamCommand


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


__all__ = [
    "build_upstream_init_commands",
]
