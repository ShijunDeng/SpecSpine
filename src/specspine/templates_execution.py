from __future__ import annotations

__all__ = [
    "EXECUTION_PLAN_TEMPLATE",
    "TASKS_TEMPLATE",
    "QUALITY_CHECKLIST_TEMPLATE",
    "REVIEW_NOTES_TEMPLATE",
]

EXECUTION_PLAN_TEMPLATE = """
    # Execution Plan

    ## Milestones

    What are the meaningful checkpoints?

    ## Work Breakdown

    What tasks need to be completed?

    ## Dependencies

    What needs to happen first?

    ## Open Questions

    What must be resolved before implementation can proceed safely?
"""

TASKS_TEMPLATE = """
    # Tasks

    - [ ] Define intent
    - [ ] Draft product spec
    - [ ] Document architecture decisions
    - [ ] Break work into implementation tasks
    - [ ] Define quality gates
"""

QUALITY_CHECKLIST_TEMPLATE = """
    # Quality Checklist

    ## Required Checks

    - [ ] Acceptance criteria are complete.
    - [ ] Tests cover the changed behavior.
    - [ ] Documentation reflects the final behavior.
    - [ ] Risks and tradeoffs are recorded.
    - [ ] Release readiness is reviewed.

    ## Definition Of Done

    What must be true before this work ships?
"""

REVIEW_NOTES_TEMPLATE = """
    # Review Notes

    ## Findings

    What issues, regressions, or risks were found?

    ## Decisions

    What changed after review?

    ## Release Notes

    What should users or operators know?
"""
