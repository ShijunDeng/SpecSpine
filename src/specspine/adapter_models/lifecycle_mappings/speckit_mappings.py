from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._openspec_factory import _build_lifecycle_mapping
from ._speckit_setup_phases import SPECKIT_SETUP_MAPPINGS
from ._speckit_delivery_phases import SPECKIT_DELIVERY_MAPPINGS

__all__ = [
    "SPECKIT_LIFECYCLE_MAPPINGS",
]

SPECKIT_LIFECYCLE_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
    *SPECKIT_SETUP_MAPPINGS,
    *SPECKIT_DELIVERY_MAPPINGS,
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
