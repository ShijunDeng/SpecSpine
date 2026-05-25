from __future__ import annotations

from ..lifecycle_constants import NATIVE_STATUS_MEANINGS, LOCAL_LIFECYCLE_COMMANDS
from ..lifecycle_models import AdapterLifecycleMapping

__all__ = [
    "_build_lifecycle_mapping",
]


def _build_lifecycle_mapping(
    adapter: str,
    status: str,
    upstream_phase: str,
    upstream_artifacts: tuple[str, ...],
    agent_focus: str,
) -> AdapterLifecycleMapping:
    return AdapterLifecycleMapping(
        id=f"{adapter}:{status}",
        status=status,
        specspine_meaning=NATIVE_STATUS_MEANINGS[status],
        upstream_phase=upstream_phase,
        upstream_artifacts=upstream_artifacts,
        agent_focus=agent_focus,
        local_commands=LOCAL_LIFECYCLE_COMMANDS[status],
    )
