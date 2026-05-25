from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._superpowers_factory import _lifecycle_mapping

__all__ = [
    "_proposed_mapping",
    "_planned_mapping",
]


def _proposed_mapping() -> AdapterLifecycleMapping:
    return _lifecycle_mapping(
        "superpowers",
        "proposed",
        "Brainstorming and requirements clarification",
        ("brainstorming notes", "requirements conversation"),
        "Challenge unclear intent and identify missing context before planning.",
    )


def _planned_mapping() -> AdapterLifecycleMapping:
    return _lifecycle_mapping(
        "superpowers",
        "planned",
        "Writing plans",
        ("implementation plan", "review checklist"),
        "Produce an executable plan with explicit risks, tasks, and validation steps.",
    )
