from __future__ import annotations

from .adapters import ADAPTER_SPECS, get_agent_profile

__all__ = [
    "_build_adapter_speckit",
]


def _build_adapter_speckit(agent: str) -> str:
    profile = get_agent_profile(agent)
    return f"""
            # Spec Kit Adapter

            Upstream: {ADAPTER_SPECS["speckit"].upstream_url}
            License: {ADAPTER_SPECS["speckit"].license_name}
            Integration mode: external Specify CLI, no vendored source code.

            ## Role

            Spec Kit owns the structured specify, plan, tasks, and implement workflow for AI coding agents.

            ## Install

            ```bash
            {ADAPTER_SPECS["speckit"].install_hint}
            ```

            ## Initialize Through SpecSpine

            ```bash
            specspine fuse . --agent {profile.key} --run-upstream
            ```

            Equivalent Spec Kit command:

            ```bash
            specify init . --integration {profile.speckit_integration}
            ```

            ## Expected Artifacts

            - `.specify/`
            - `specs/`
            - agent-specific command or skill files

            SpecSpine keeps a higher-level backbone and lets Spec Kit manage its own generated agent integration files.
        """
