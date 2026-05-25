from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._superpowers_status_mappings import (
    _proposed_mapping,
    _planned_mapping,
    _in_progress_mapping,
    _implemented_mapping,
    _validated_mapping,
    _archived_mapping,
)

__all__ = [
    "SUPERPOWERS_LIFECYCLE_MAPPINGS",
]

SUPERPOWERS_LIFECYCLE_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
    _proposed_mapping(),
    _planned_mapping(),
    _in_progress_mapping(),
    _implemented_mapping(),
    _validated_mapping(),
    _archived_mapping(),
)
