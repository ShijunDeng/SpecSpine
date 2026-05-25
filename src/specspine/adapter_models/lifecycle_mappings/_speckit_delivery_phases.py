from __future__ import annotations

from ..lifecycle_models import AdapterLifecycleMapping
from ._openspec_factory import _build_lifecycle_mapping

__all__ = [
    "SPECKIT_DELIVERY_MAPPINGS",
]

SPECKIT_DELIVERY_MAPPINGS: tuple[AdapterLifecycleMapping, ...] = (
    _build_lifecycle_mapping(
        "speckit",
        "in-progress",
        "Tasks and implement phase",
        ("specs/<feature>/tasks.md", "implementation files"),
        "Drive implementation from the task list while preserving spec traceability.",
    ),
    _build_lifecycle_mapping(
        "speckit",
        "implemented",
        "Implementation complete against tasks",
        ("specs/<feature>/tasks.md", "source changes", "documentation updates"),
        "Check that planned tasks landed before final quality validations.",
    ),
    _build_lifecycle_mapping(
        "speckit",
        "validated",
        "Checklist, analyze, and governance checks passed",
        ("specs/<feature>/checklists/", "constitution checks", "test evidence"),
        "Use checklist and analysis evidence to confirm the implementation matches the spec.",
    ),
    _build_lifecycle_mapping(
        "speckit",
        "archived",
        "Feature folder retained as release history",
        ("specs/<feature>/", "release notes"),
        "Keep completed spec, plan, tasks, and evidence available for future agents.",
    ),
)
