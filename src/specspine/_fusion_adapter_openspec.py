from __future__ import annotations

from .adapters import ADAPTER_SPECS, get_agent_profile

__all__ = [
    "_build_adapter_openspec",
]


def _build_adapter_openspec(agent: str) -> str:
    profile = get_agent_profile(agent)
    return f"""
            # OpenSpec Adapter

            Upstream: {ADAPTER_SPECS["openspec"].upstream_url}
            License: {ADAPTER_SPECS["openspec"].license_name}
            Integration mode: external CLI, no vendored source code.

            ## Role

            OpenSpec owns lightweight change proposals, spec deltas, design notes, task lists, validation, and archive flow.

            ## Install

            ```bash
            {ADAPTER_SPECS["openspec"].install_hint}
            ```

            ## Initialize Through SpecSpine

            ```bash
            specspine fuse . --agent {profile.key} --run-upstream
            ```

            Equivalent OpenSpec command:

            ```bash
            openspec init . --tools {profile.openspec_tool}
            ```

            ## Expected Artifacts

            - `openspec/specs/`
            - `openspec/changes/`
            - `openspec/config.yaml`

            SpecSpine references these artifacts but does not replace OpenSpec's own lifecycle.
        """
