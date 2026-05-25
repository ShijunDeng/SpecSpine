from __future__ import annotations

from .adapters import get_agent_profile


def _build_fusion_map(
    agent: str,
    *,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
) -> str:
    profile = get_agent_profile(agent)
    enabled_keys = [
        key
        for key, enabled in (
            ("openspec", include_openspec),
            ("speckit", include_speckit),
            ("superpowers", include_superpowers),
        )
        if enabled
    ]

    return f"""
            # SpecSpine Fusion Map

            SpecSpine is the project-local backbone. It does not vendor OpenSpec, Spec Kit, or Superpowers code. It records how those tools are connected and invokes them through their public installation and command surfaces.

            ## Enabled Upstreams

            {", ".join(enabled_keys) if enabled_keys else "none"}

            ## Responsibility Split

            | Layer | SpecSpine Role | Upstream Role |
            | --- | --- | --- |
            | Why | Keep intent, users, constraints, and outcome signals in `specs/intent.md`. | Spec Kit's specify phase and OpenSpec proposals sharpen the "what" and "why". |
            | What | Keep product scope, non-goals, workflows, and acceptance criteria in `specs/product.md`. | Spec Kit specs and OpenSpec spec deltas provide detailed requirements artifacts. |
            | How | Keep architectural decisions and execution plans in `specs/architecture.md` and `execution/plan.md`. | Spec Kit plan/tasks and OpenSpec design/tasks drive implementation structure. |
            | Finish Well | Keep quality gates, review notes, and release readiness in `quality/`. | Superpowers provides brainstorming, writing-plans, TDD, subagent execution, code review, and verification discipline. |

            ## Agent Profile

            - Agent: `{profile.key}`
            - OpenSpec tool id: `{profile.openspec_tool}`
            - Spec Kit integration key: `{profile.speckit_integration}`
            - Superpowers: {profile.superpowers_hint}

            ## Operating Rule

            When upstream files and SpecSpine files disagree, treat it as spec drift. Resolve the discrepancy in the spec layer before implementation continues.
        """


__all__ = [
    "_build_fusion_map",
]
