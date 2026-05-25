from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._openspec_factory import _build_lifecycle_mapping

__all__ = [
    "OPENSCPEC_SETUP_MAPPINGS",
]

OPENSCPEC_SETUP_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
    _build_lifecycle_mapping(
        "openspec",
        "proposed",
        "Change proposal drafted",
        ("openspec/changes/<change-id>/proposal.md", "openspec/changes/<change-id>/specs/"),
        "Clarify why the change exists and what capability delta it proposes.",
    ),
    _build_lifecycle_mapping(
        "openspec",
        "planned",
        "Design and task plan ready",
        (
            "openspec/changes/<change-id>/proposal.md",
            "openspec/changes/<change-id>/design.md",
            "openspec/changes/<change-id>/tasks.md",
            "openspec/changes/<change-id>/specs/",
        ),
        "Review design tradeoffs, spec deltas, and ordered tasks before implementation.",
    ),
)
