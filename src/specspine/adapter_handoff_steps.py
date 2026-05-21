from __future__ import annotations

from typing import Iterable

from .adapter_models import (
    ADAPTER_LIFECYCLE_MAPPINGS,
    AdapterHandoffStep,
    AdapterLifecycleMapping,
)

__all__ = [
    "_adapter_handoff_recommended_commands",
    "_mapping_for_status",
    "_openspec_steps",
    "_recommended_steps",
    "_replace_slug",
    "_speckit_steps",
    "_superpowers_steps",
]


def _replace_slug(commands: Iterable[str], slug: str) -> tuple[str, ...]:
    return tuple(command.replace("<slug>", slug) for command in commands)


def _mapping_for_status(
    adapter_key: str,
    status: str,
) -> AdapterLifecycleMapping | None:
    for mapping in ADAPTER_LIFECYCLE_MAPPINGS[adapter_key]:
        if mapping.status == status:
            return mapping
    return None


def _openspec_steps(slug: str) -> tuple[AdapterHandoffStep, ...]:
    return (
        AdapterHandoffStep(
            id="openspec.status-json",
            kind="cli-command",
            description="Review OpenSpec change and spec status as JSON.",
            argv=("openspec", "status", "--json"),
        ),
        AdapterHandoffStep(
            id="openspec.instructions-apply",
            kind="cli-command",
            description="Apply OpenSpec agent instructions for the matching change id.",
            argv=(
                "openspec",
                "instructions",
                "apply",
                "--change",
                slug,
                "--json",
            ),
        ),
        AdapterHandoffStep(
            id="openspec.validate-all-json",
            kind="cli-command",
            description="Validate all OpenSpec artifacts and return JSON findings.",
            argv=("openspec", "validate", "--all", "--json"),
        ),
    )


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


def _recommended_steps(adapter_key: str, slug: str) -> tuple[AdapterHandoffStep, ...]:
    if adapter_key == "openspec":
        return _openspec_steps(slug)
    if adapter_key == "speckit":
        return _speckit_steps(slug)
    if adapter_key == "superpowers":
        return _superpowers_steps(slug)
    return ()


def _adapter_handoff_recommended_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature handoff {slug} . --json",
        "specspine adapters lifecycle . --json",
        f"specspine feature ready {slug} . --json",
        "specspine validate . --fusion --features",
    )
