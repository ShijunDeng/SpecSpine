from __future__ import annotations

__all__ = [
    "EXECUTION_PLAN_TEMPLATE",
    "TASKS_TEMPLATE",
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
