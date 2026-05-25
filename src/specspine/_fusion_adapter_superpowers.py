from __future__ import annotations

from .adapters import ADAPTER_SPECS, get_agent_profile

__all__ = [
    "_build_adapter_superpowers",
    "_build_quality_superpowers",
]


def _build_adapter_superpowers(agent: str) -> str:
    profile = get_agent_profile(agent)
    return f"""
            # Superpowers Adapter

            Upstream: {ADAPTER_SPECS["superpowers"].upstream_url}
            License: {ADAPTER_SPECS["superpowers"].license_name}
            Integration mode: installed agent plugin/extension, no vendored source code.

            ## Role

            Superpowers is the quality discipline layer. SpecSpine expects the agent to use Superpowers skills for:

            - brainstorming
            - writing-plans
            - test-driven-development
            - subagent-driven-development or executing-plans
            - requesting-code-review
            - verification-before-completion
            - finishing-a-development-branch

            ## Install

            {profile.superpowers_hint}

            ## Contract

            SpecSpine does not copy skill files. It records that Superpowers should be installed in the active AI coding agent and uses `quality/superpowers.md` as the project-local policy bridge.
        """


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
