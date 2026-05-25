from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "AdapterSpec",
    "ADAPTER_SPECS",
]


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
