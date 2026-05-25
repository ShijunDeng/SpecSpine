from __future__ import annotations

from .feature_bundle import FeatureSyncPlanCommand

__all__ = [
    "_sync_command",
]


def _sync_command(
    *,
    command_id: str,
    kind: str,
    description: str,
    argv: tuple[str, ...],
    body_source: str,
    body: str,
) -> FeatureSyncPlanCommand:
    return FeatureSyncPlanCommand(
        id=command_id,
        kind=kind,
        description=description,
        argv=argv,
        body_source=body_source,
        body=body,
    )
