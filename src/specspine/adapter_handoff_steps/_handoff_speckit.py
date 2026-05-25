from __future__ import annotations

from ..adapter_models import AdapterHandoffStep

__all__ = [
    "_speckit_steps",
]


def _speckit_steps(slug: str) -> tuple[AdapterHandoffStep, ...]:
    return (
        AdapterHandoffStep(
            id="speckit.spec",
            kind="agent-action",
            description="Prepare or review the Spec Kit spec artifact for this feature.",
            instruction=(
                f"Use Spec Kit's Spec phase for `{slug}` to capture scenarios, "
                "acceptance criteria, constraints, and user value from the local "
                "SpecSpine feature bundle."
            ),
        ),
        AdapterHandoffStep(
            id="speckit.plan",
            kind="agent-action",
            description="Prepare or review the Spec Kit plan artifact.",
            instruction=(
                f"Use Spec Kit's Plan phase for `{slug}` to turn the spec into "
                "architecture, research, contracts, and implementation shape."
            ),
        ),
        AdapterHandoffStep(
            id="speckit.tasks",
            kind="agent-action",
            description="Prepare or review the Spec Kit tasks artifact.",
            instruction=(
                f"Use Spec Kit's Tasks phase for `{slug}` to produce an ordered "
                "task list that traces back to the spec and plan artifacts."
            ),
        ),
        AdapterHandoffStep(
            id="speckit.implement",
            kind="agent-action",
            description="Hand the Spec Kit implement phase to an agent without running it from SpecSpine.",
            instruction=(
                f"Use Spec Kit's Implement phase for `{slug}` only after the "
                "Spec, Plan, and Tasks artifacts are reviewed as local context."
            ),
        ),
    )
