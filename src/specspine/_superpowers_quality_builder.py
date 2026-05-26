from __future__ import annotations

__all__ = [
    "_build_quality_superpowers",
]


def _build_quality_superpowers() -> str:
    return """
            # Superpowers Quality Policy

            Use Superpowers as the quality discipline layer for SpecSpine work.

            ## Before Implementation

            - Use brainstorming to refine unclear intent.
            - Use writing-plans to create task-level implementation plans.
            - Confirm acceptance criteria are present before writing code.

            ## During Implementation

            - Prefer test-driven-development for behavior changes.
            - Keep tasks traceable to the current spec and plan.
            - Use subagent-driven-development or executing-plans for multi-step work.

            ## Before Completion

            - Run verification-before-completion.
            - Request code review against the spec and implementation plan.
            - Record unresolved findings in `quality/review.md`.
        """
