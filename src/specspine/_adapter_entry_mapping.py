from __future__ import annotations

from .adapter_handoff_steps import (
    _mapping_for_status,
)
from ._handoff_slug_utils import _replace_slug_local

__all__ = [
    "_resolve_adapter_mapping",
]


def _resolve_adapter_mapping(
    adapter_key: str,
    status: str,
    slug: str,
) -> tuple[str, tuple[str, ...], str, tuple[str, ...], tuple[str, ...]]:
    mapping = _mapping_for_status(adapter_key, status)
    if mapping is None:
        upstream_phase = "No mapping selected"
        upstream_artifacts: tuple[str, ...] = ()
        agent_focus = (
            "Resolve the native feature status before handing work to this adapter."
        )
        local_commands: tuple[str, ...] = ()
        notes = (
            f"Native status `{status}` has no adapter lifecycle mapping.",
            "SpecSpine did not execute upstream tools or inspect adapter runtime availability.",
        )
    else:
        upstream_phase = mapping.upstream_phase
        upstream_artifacts = mapping.upstream_artifacts
        agent_focus = mapping.agent_focus
        local_commands = _replace_slug_local(mapping.local_commands, slug)
        notes = (
            f"Selected mapping `{mapping.id}` for native status `{status}`.",
            "Recommended upstream steps are handoff data only; SpecSpine did not execute them.",
        )
    return upstream_phase, upstream_artifacts, agent_focus, local_commands, notes
