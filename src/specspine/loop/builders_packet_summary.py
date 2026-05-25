from __future__ import annotations

from typing import Any

__all__ = [
    "_summary",
]


def _summary(status: dict[str, Any], core_features: list[dict[str, object]]) -> dict[str, int]:
    readiness = status.get("readiness_summary", {})
    if not isinstance(readiness, dict):
        readiness = {}
    upstreams = status.get("upstreams", {})
    if not isinstance(upstreams, dict):
        upstreams = {}

    return {
        "features_total": len(core_features),
        "features_ready": int(readiness.get("ready", 0)),
        "features_not_ready": int(readiness.get("not_ready", 0)),
        "tasks_open_total": sum(
            int(feature.get("tasks_summary", {}).get("open", 0))
            for feature in core_features
            if isinstance(feature.get("tasks_summary", {}), dict)
        ),
        "gaps_total": int(readiness.get("gaps_total", 0)),
        "blocking_checks_total": int(readiness.get("blocking_checks_total", 0)),
        "enabled_upstreams": sum(
            1
            for upstream in upstreams.values()
            if isinstance(upstream, dict) and bool(upstream.get("enabled", False))
        ),
    }
