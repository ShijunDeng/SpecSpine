from __future__ import annotations

from ..adapter_models import AdapterHandoffStep

__all__ = [
    "_superpowers_steps",
]


def _superpowers_steps(_slug: str) -> tuple[AdapterHandoffStep, ...]:
    return (
        AdapterHandoffStep(
            id="superpowers.brainstorming",
            kind="agent-action",
            description="Use brainstorming to clarify intent and unresolved questions.",
            instruction="Apply the brainstorming skill before locking requirements or scope.",
        ),
        AdapterHandoffStep(
            id="superpowers.writing-plans",
            kind="agent-action",
            description="Use writing-plans to produce an executable implementation plan.",
            instruction="Apply the writing-plans skill and keep risks, tasks, and validation explicit.",
        ),
        AdapterHandoffStep(
            id="superpowers.test-driven-development",
            kind="agent-action",
            description="Use test-driven-development for behavior changes.",
            instruction="Apply test-driven-development so tests lead implementation where practical.",
        ),
        AdapterHandoffStep(
            id="superpowers.subagent-driven-development",
            kind="agent-action",
            description="Use subagent-driven-development for parallel review or implementation slices.",
            instruction="Apply subagent-driven-development when focused subagent handoffs reduce risk.",
        ),
        AdapterHandoffStep(
            id="superpowers.requesting-code-review",
            kind="agent-action",
            description="Use requesting-code-review before completion.",
            instruction="Apply requesting-code-review and capture findings in local review evidence.",
        ),
        AdapterHandoffStep(
            id="superpowers.verification-before-completion",
            kind="agent-action",
            description="Use verification-before-completion before marking the feature done.",
            instruction="Apply verification-before-completion and record the checks that passed.",
        ),
    )
