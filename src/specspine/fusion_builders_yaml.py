from __future__ import annotations

from .adapters import (
    ADAPTER_SPECS,
    build_upstream_init_commands,
    get_agent_profile,
)


def _build_fusion_yaml(
    agent: str,
    *,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
) -> str:
    profile = get_agent_profile(agent)

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
    upstream_init_yaml = "\n".join(command_lines) if command_lines else "  []"

    return "\n".join(
        [
            "name: SpecSpine Fusion",
            "version: 0.1",
            "integration_mode: adapter",
            "vendored_upstream_code: false",
            "agent:",
            f"  key: {profile.key}",
            f"  openspec_tool: {profile.openspec_tool}",
            f"  speckit_integration: {profile.speckit_integration}",
            "upstreams:",
            "  openspec:",
            f"    enabled: {str(include_openspec).lower()}",
            f"    role: \"{ADAPTER_SPECS['openspec'].role}\"",
            f"    repo: \"{ADAPTER_SPECS['openspec'].upstream_url}\"",
            f"    license: \"{ADAPTER_SPECS['openspec'].license_name}\"",
            "    adapter: \".specspine/adapters/openspec.md\"",
            "  speckit:",
            f"    enabled: {str(include_speckit).lower()}",
            f"    role: \"{ADAPTER_SPECS['speckit'].role}\"",
            f"    repo: \"{ADAPTER_SPECS['speckit'].upstream_url}\"",
            f"    license: \"{ADAPTER_SPECS['speckit'].license_name}\"",
            "    adapter: \".specspine/adapters/speckit.md\"",
            "  superpowers:",
            f"    enabled: {str(include_superpowers).lower()}",
            f"    role: \"{ADAPTER_SPECS['superpowers'].role}\"",
            f"    repo: \"{ADAPTER_SPECS['superpowers'].upstream_url}\"",
            f"    license: \"{ADAPTER_SPECS['superpowers'].license_name}\"",
            "    adapter: \".specspine/adapters/superpowers.md\"",
            "workflow:",
            "  intent: [\"specs/intent.md\", \"openspec proposal\", \"speckit specify\"]",
            "  product_spec: [\"specs/product.md\", \"speckit specify\", \"openspec specs\"]",
            "  architecture: [\"specs/architecture.md\", \"openspec design\", \"speckit plan\"]",
            "  execution: [\"execution/plan.md\", \"execution/tasks.md\", \"speckit tasks\"]",
            "  quality: [\"quality/checklist.md\", \"quality/superpowers.md\", \"superpowers skills\"]",
            "upstream_init:",
            upstream_init_yaml,
            "",
        ]
    )


__all__ = [
    "_build_fusion_yaml",
]
