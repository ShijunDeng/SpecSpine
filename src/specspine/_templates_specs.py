from __future__ import annotations

__all__ = [
    "INTENT_TEMPLATE",
    "PRODUCT_TEMPLATE",
    "ARCHITECTURE_TEMPLATE",
]

INTENT_TEMPLATE = """
    # Intent

    ## Why

    What problem are we solving, and why does it matter now?

    ## Users

    Who benefits from this work?

    ## Outcomes

    What measurable signals show that the work succeeded?

    ## Constraints

    What business, technical, legal, operational, or timing constraints shape the solution?
"""

PRODUCT_TEMPLATE = """
    # Product Spec

    ## Scope

    What should be built?

    ## Non-Goals

    What is explicitly out of scope?

    ## User Workflows

    What should users be able to do from start to finish?

    ## Acceptance Criteria

    What must be true before this work is considered complete?
"""

ARCHITECTURE_TEMPLATE = """
    # Architecture

    ## System Shape

    What are the major components and boundaries?

    ## Data And Interfaces

    What data structures, APIs, files, commands, or events matter?

    ## Decisions

    What decisions have been made, and why?

    ## Risks

    What can break the plan, and how will it be handled?
"""
