from __future__ import annotations

from ..lifecycle_constants import NATIVE_STATUS_MEANINGS, LOCAL_LIFECYCLE_COMMANDS
from ..lifecycle_models import AdapterLifecycleMapping
from .openspec_mappings import OPENSCPEC_LIFECYCLE_MAPPINGS, _lifecycle_mapping as _openspec_mapping
from .speckit_mappings import SPECKIT_LIFECYCLE_MAPPINGS
from .superpowers_mappings import SUPERPOWERS_LIFECYCLE_MAPPINGS

__all__ = [
    "_lifecycle_mapping",
    "ADAPTER_LIFECYCLE_MAPPINGS",
]


def _lifecycle_mapping(
    adapter: str,
    status: str,
    upstream_phase: str,
    upstream_artifacts: tuple[str, ...],
    agent_focus: str,
) -> AdapterLifecycleMapping:
    return AdapterLifecycleMapping(
        id=f"{adapter}:{status}",
        status=status,
        specspine_meaning=NATIVE_STATUS_MEANINGS[status],
        upstream_phase=upstream_phase,
        upstream_artifacts=upstream_artifacts,
        agent_focus=agent_focus,
        local_commands=LOCAL_LIFECYCLE_COMMANDS[status],
    )


ADAPTER_LIFECYCLE_MAPPINGS: dict[str, tuple[AdapterLifecycleMapping, ...]] = {
    "openspec": OPENSCPEC_LIFECYCLE_MAPPINGS,
    "speckit": SPECKIT_LIFECYCLE_MAPPINGS,
    "superpowers": SUPERPOWERS_LIFECYCLE_MAPPINGS,
}
