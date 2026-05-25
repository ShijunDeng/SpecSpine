from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._openspec_factory import _build_lifecycle_mapping

__all__ = [
    "OPENSCPEC_DELIVERY_MAPPINGS",
]

OPENSCPEC_DELIVERY_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
    _build_lifecycle_mapping(
        "openspec",
        "in-progress",
        "Change implementation active",
        ("openspec/changes/<change-id>/tasks.md", "openspec/changes/<change-id>/specs/"),
        "Keep implementation work tied to the approved change tasks and spec deltas.",
    ),
    _build_lifecycle_mapping(
        "openspec",
        "implemented",
        "Change artifacts complete before validation",
        ("openspec/changes/<change-id>/tasks.md", "openspec/changes/<change-id>/design.md"),
        "Confirm tasks and implementation evidence are complete before validation.",
    ),
    _build_lifecycle_mapping(
        "openspec",
        "validated",
        "OpenSpec validation and review passed",
        ("openspec validate --all", "openspec/changes/<change-id>/"),
        "Use validation findings to close drift between proposal, specs, and code.",
    ),
    _build_lifecycle_mapping(
        "openspec",
        "archived",
        "Change archived into living specs",
        ("openspec/specs/", "openspec/changes/archive/"),
        "Retain the accepted change history after the living specs are updated.",
    ),
)
