from __future__ import annotations

from ..adapters import get_agent_profile
from ._yaml_builders_commands import _format_upstream_init_yaml
from ._yaml_builders_upstream import _build_upstream_sections

__all__ = [
    "_build_fusion_yaml",
]


def _build_fusion_yaml(
    agent: str,
    *,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
) -> str:
    profile = get_agent_profile(agent)

    upstream_init_yaml = _format_upstream_init_yaml(
        agent=agent,
        include_openspec=include_openspec,
        include_speckit=include_speckit,
        include_superpowers=include_superpowers,
    )

    upstream_sections = _build_upstream_sections(
        include_openspec=include_openspec,
        include_speckit=include_speckit,
        include_superpowers=include_superpowers,
    )

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
            upstream_sections,
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
