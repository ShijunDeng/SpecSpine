from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._openspec_factory import _build_lifecycle_mapping
from ._openspec_setup_phases import OPENSCPEC_SETUP_MAPPINGS
from ._openspec_delivery_phases import OPENSCPEC_DELIVERY_MAPPINGS

__all__ = [
    "OPENSCPEC_LIFECYCLE_MAPPINGS",
]

OPENSCPEC_LIFECYCLE_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
    *OPENSCPEC_SETUP_MAPPINGS,
    *OPENSCPEC_DELIVERY_MAPPINGS,
)


def _lifecycle_mapping(
    adapter: str,
    status: str,
    upstream_phase: str,
    upstream_artifacts: tuple[str, ...],
    agent_focus: str,
) -> AdapterLifecycleMapping:
    return _build_lifecycle_mapping(
        adapter, status, upstream_phase, upstream_artifacts, agent_focus,
    )
