from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._superpowers_factory import _lifecycle_mapping

__all__ = [
    "_validated_mapping",
    "_archived_mapping",
]


def _validated_mapping() -> AdapterLifecycleMapping:
    return _lifecycle_mapping(
        "superpowers",
        "validated",
        "Verification before completion",
        ("verification results", "code review findings", "release readiness notes"),
        "Confirm tests, review, and completion evidence before handing off.",
    )


def _archived_mapping() -> AdapterLifecycleMapping:
    return _lifecycle_mapping(
        "superpowers",
        "archived",
        "Finishing a development branch",
        ("completion notes", "merged or closed branch record"),
        "Preserve the final evidence and any follow-up notes for future work.",
    )
