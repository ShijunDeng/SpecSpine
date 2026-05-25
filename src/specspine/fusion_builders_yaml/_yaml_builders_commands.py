from __future__ import annotations

from ..adapters import build_upstream_init_commands

__all__ = [
    "_format_upstream_init_yaml",
]


def _format_upstream_init_yaml(
    *,
    agent: str,
    include_openspec: bool,
    include_speckit: bool,
    include_superpowers: bool,
) -> str:
    commands = build_upstream_init_commands(
        agent=agent,
        include_openspec=include_openspec,
        include_speckit=include_speckit,
        include_superpowers=include_superpowers,
    )
    command_lines = [
        f"  - {command.key}: \"{command.display() or command.description}\""
        for command in commands
    ]
    return "\n".join(command_lines) if command_lines else "  []"
