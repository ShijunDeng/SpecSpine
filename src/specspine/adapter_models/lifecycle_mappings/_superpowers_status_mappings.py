from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._superpowers_factory import _lifecycle_mapping

__all__ = [
    "_proposed_mapping",
    "_planned_mapping",
    "_in_progress_mapping",
    "_implemented_mapping",
    "_validated_mapping",
    "_archived_mapping",
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


def _in_progress_mapping() -> AdapterLifecycleMapping:
    return _lifecycle_mapping(
        "superpowers",
        "in-progress",
        "TDD and subagent-driven development",
        ("tests", "task progress", "subagent handoffs"),
        "Keep tests, implementation, and subagent feedback aligned with the plan.",
    )


def _implemented_mapping() -> AdapterLifecycleMapping:
    return _lifecycle_mapping(
        "superpowers",
        "implemented",
        "Development branch ready for review",
        ("code changes", "test results", "review request"),
        "Request review against the original plan and surface unresolved risks.",
    )


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
