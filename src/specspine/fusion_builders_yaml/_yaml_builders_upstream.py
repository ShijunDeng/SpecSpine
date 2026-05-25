from __future__ import annotations

from ..adapters import ADAPTER_SPECS

__all__ = [
    "_build_upstream_sections",
]


def _build_upstream_section(key: str, enabled: bool) -> str:
    spec = ADAPTER_SPECS[key]
    adapter_path = ".specspine/adapters/"
    if key == "openspec":
        adapter_path += "openspec.md"
    elif key == "speckit":
        adapter_path += "speckit.md"
    elif key == "superpowers":
        adapter_path += "superpowers.md"
    return "\n".join([
        f"  {key}:",
        f"    enabled: {str(enabled).lower()}",
        f"    role: \"{spec.role}\"",
        f"    repo: \"{spec.upstream_url}\"",
        f"    license: \"{spec.license_name}\"",
        f"    adapter: \"{adapter_path}\"",
    ])


def _build_upstream_sections(
    *,
    include_openspec: bool,
    include_speckit: bool,
    include_superpowers: bool,
) -> str:
    return "\n".join([
        "upstreams:",
        _build_upstream_section("openspec", include_openspec),
        _build_upstream_section("speckit", include_speckit),
        _build_upstream_section("superpowers", include_superpowers),
    ])
