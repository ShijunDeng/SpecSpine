from __future__ import annotations

from typing import Iterable

from ..adapter_models import AdapterHandoffStep

__all__ = [
    "_openspec_steps",
]


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
