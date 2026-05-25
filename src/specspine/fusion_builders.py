from __future__ import annotations

from .adapters import get_agent_profile
from .fusion_builders_adapters import (
    _build_adapter_openspec,
    _build_adapter_speckit,
    _build_adapter_superpowers,
    _build_quality_superpowers,
)
from .fusion_builders_map import _build_fusion_map
from .fusion_builders_yaml import _build_fusion_yaml


def build_fusion_files(
    agent: str,
    *,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
) -> dict[str, str]:
    profile = get_agent_profile(agent)
    enabled_keys = [
        key
        for key, enabled in (
            ("openspec", include_openspec),
            ("speckit", include_speckit),
            ("superpowers", include_superpowers),
        )
        if enabled
    ]

    files: dict[str, str] = {
        ".specspine/fusion.yaml": _build_fusion_yaml(
            agent,
            include_openspec=include_openspec,
            include_speckit=include_speckit,
            include_superpowers=include_superpowers,
        ),
        ".specspine/fusion-map.md": _build_fusion_map(
            agent,
            include_openspec=include_openspec,
            include_speckit=include_speckit,
            include_superpowers=include_superpowers,
        ),
        ".specspine/adapters/openspec.md": _build_adapter_openspec(agent),
        ".specspine/adapters/speckit.md": _build_adapter_speckit(agent),
        ".specspine/adapters/superpowers.md": _build_adapter_superpowers(agent),
        "quality/superpowers.md": _build_quality_superpowers(),
    }

    return files


__all__ = [
    "build_fusion_files",
]
