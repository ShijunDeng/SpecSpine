from __future__ import annotations

__all__ = [
    "NATIVE_STATUS_MEANINGS",
    "LOCAL_LIFECYCLE_COMMANDS",
]

NATIVE_STATUS_MEANINGS: dict[str, str] = {
    "proposed": "Intent and scope are captured, but the implementation plan is not committed yet.",
    "planned": "Architecture, task shape, and quality gates are ready for implementation.",
    "in-progress": "Implementation is underway against the accepted local plan.",
    "implemented": "Code and documentation are written and waiting for validation evidence.",
    "validated": "Local checks, review evidence, and release readiness are complete.",
    "archived": "The work is complete or closed and retained as historical context.",
}

LOCAL_LIFECYCLE_COMMANDS: dict[str, tuple[str, ...]] = {
    "proposed": (
        'specspine feature new <slug> . --title "..." --why "..."',
        "specspine feature status <slug> . --set planned --enforce-transition --json",
    ),
    "planned": (
        "specspine feature handoff <slug> . --json",
        "specspine feature tasks <slug> . --json",
    ),
    "in-progress": (
        "specspine feature tasks <slug> . --json",
        "specspine feature trace <slug> . --json",
    ),
    "implemented": (
        "specspine feature tests <slug> . --json",
        "specspine feature ready <slug> . --json",
    ),
    "validated": (
        "specspine feature pr <slug> . --json",
        "specspine validate . --fusion --features",
    ),
    "archived": (
        "specspine feature status <slug> . --set archived --enforce-transition --json",
        "specspine status . --json --validate",
    ),
}
