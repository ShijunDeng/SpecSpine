from __future__ import annotations

from pathlib import Path
from typing import Any

from ..fusion import FUSION_REQUIRED_FILES

__all__ = [
    "_build_recommendations",
]


def _build_recommendations(
    *,
    root: Path,
    workspace_missing: list[str],
    fusion_missing: list[str],
    upstreams: dict[str, dict[str, Any]],
    adapters: dict[str, dict[str, Any]] | None,
) -> list[str]:
    recommendations: list[str] = []

    if workspace_missing:
        recommendations.append(f"Run `specspine init {root}` to create missing workspace artifacts.")

    fusion_specific_missing = [
        path for path in fusion_missing if path in FUSION_REQUIRED_FILES
    ]
    if fusion_specific_missing:
        recommendations.append(
            f"Run `specspine fuse {root} --agent codex` to create or repair fusion artifacts."
        )

    enabled_upstreams = [
        key for key, upstream in upstreams.items() if bool(upstream["enabled"])
    ]
    if not enabled_upstreams:
        recommendations.append(
            "Run `specspine fuse <path> --agent codex` when OpenSpec, Spec Kit, or Superpowers integration is needed."
        )

    if adapters is not None:
        for key in enabled_upstreams:
            adapter = adapters.get(key)
            if adapter and not adapter["available"]:
                recommendations.append(
                    f"Install {adapter['display_name']}: {adapter['install_hint']}"
                )

    if not recommendations:
        recommendations.append("Use `specspine status --json` as the compact context packet for agents.")

    return recommendations
