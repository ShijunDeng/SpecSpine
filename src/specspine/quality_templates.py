from __future__ import annotations

__all__ = [
    "QUALITY_CHECKLIST_TEMPLATE",
    "REVIEW_NOTES_TEMPLATE",
]

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
