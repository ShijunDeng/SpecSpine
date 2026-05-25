from __future__ import annotations

__all__ = [
    "VALIDATION_STATUSES",
    "WORKSPACE_PLACEHOLDER_PHRASES",
]

VALIDATION_STATUSES = ("pass", "fail", "warn", "skip")

WORKSPACE_PLACEHOLDER_PHRASES: dict[str, tuple[str, ...]] = {
    "specs/intent.md": (
        "What problem are we solving, and why does it matter now?",
        "Who benefits from this work?",
        "What measurable signals show that the work succeeded?",
        "What business, technical, legal, operational, or timing constraints shape the solution?",
    ),
    "specs/product.md": (
        "What should be built?",
        "What is explicitly out of scope?",
        "What should users be able to do from start to finish?",
        "What must be true before this work is considered complete?",
    ),
    "specs/architecture.md": (
        "What are the major components and boundaries?",
        "What data structures, APIs, files, commands, or events matter?",
        "What decisions have been made, and why?",
        "What can break the plan, and how will it be handled?",
    ),
    "execution/plan.md": (
        "What are the meaningful checkpoints?",
        "What tasks need to be completed?",
        "What needs to happen first?",
        "What must be resolved before implementation can proceed safely?",
    ),
    "execution/tasks.md": (
        "Define intent",
        "Draft product spec",
        "Document architecture decisions",
        "Break work into implementation tasks",
        "Define quality gates",
    ),
    "quality/checklist.md": (
        "Acceptance criteria are complete.",
        "Tests cover the changed behavior.",
        "Documentation reflects the final behavior.",
        "Risks and tradeoffs are recorded.",
        "Release readiness is reviewed.",
        "What must be true before this work ships?",
    ),
    "quality/review.md": (
        "What issues, regressions, or risks were found?",
        "What changed after review?",
        "What should users or operators know?",
    ),
}
