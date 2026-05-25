from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._superpowers_factory import _lifecycle_mapping

__all__ = [
    "_in_progress_mapping",
    "_implemented_mapping",
]


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
