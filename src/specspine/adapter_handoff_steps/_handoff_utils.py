from __future__ import annotations

from typing import Iterable

from ..adapter_models import (
    ADAPTER_LIFECYCLE_MAPPINGS,
    AdapterLifecycleMapping,
)

__all__ = [
    "_adapter_handoff_recommended_commands",
    "_mapping_for_status",
    "_replace_slug",
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


def _adapter_handoff_recommended_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature handoff {slug} . --json",
        "specspine adapters lifecycle . --json",
        f"specspine feature ready {slug} . --json",
        "specspine validate . --fusion --features",
    )
