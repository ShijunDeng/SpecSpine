from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._openspec_factory import _build_lifecycle_mapping

__all__ = [
    "SPECKIT_SETUP_MAPPINGS",
]

SPECKIT_SETUP_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
    _build_lifecycle_mapping(
        "speckit",
        "proposed",
        "Spec phase",
        ("specs/<feature>/spec.md", ".specify/"),
        "Capture user value, scenarios, constraints, and acceptance criteria.",
    ),
    _build_lifecycle_mapping(
        "speckit",
        "planned",
        "Plan phase",
        (
            "specs/<feature>/plan.md",
            "specs/<feature>/research.md",
            "specs/<feature>/data-model.md",
            "specs/<feature>/contracts/",
        ),
        "Turn the spec into architecture, research, contracts, and implementation shape.",
    ),
)
