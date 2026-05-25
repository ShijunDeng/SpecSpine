from __future__ import annotations

from pathlib import Path

from .adapter_models import (
    ADAPTER_LIFECYCLE_MAPPINGS,
    ADAPTER_SPECS,
    AdapterLifecycleAdapter,
    AdapterLifecycleReport,
)
from .features import FEATURE_STATUSES
from .adapter_lifecycle_fusion_config import _read_fusion_upstreams
from .adapter_lifecycle_renderers import render_adapter_lifecycle_json, render_adapter_lifecycle_text

__all__ = [
    "build_adapter_lifecycle_report",
    "render_adapter_lifecycle_json",
    "render_adapter_lifecycle_text",
]


def _adapter_lifecycle_recommended_commands() -> tuple[str, ...]:
    return (
        "specspine status . --json --validate",
        "specspine adapters doctor",
        "specspine validate . --fusion --features",
    )


def build_adapter_lifecycle_report(root: Path) -> AdapterLifecycleReport:
    resolved_root = root.expanduser().resolve()
    fusion_upstreams = _read_fusion_upstreams(resolved_root)
    adapters: dict[str, AdapterLifecycleAdapter] = {}

    for key, spec in ADAPTER_SPECS.items():
        fusion_config = fusion_upstreams.get(key, {})
        adapter_path = fusion_config.get("adapter")
        if not isinstance(adapter_path, str) or not adapter_path:
            adapter_path = f".specspine/adapters/{key}.md"

        enabled = fusion_config.get("enabled", False)
        if not isinstance(enabled, bool):
            enabled = False

        adapters[key] = AdapterLifecycleAdapter(
            key=key,
            display_name=spec.display_name,
            enabled=enabled,
            config=adapter_path,
            config_exists=(resolved_root / adapter_path).exists(),
            upstream_url=spec.upstream_url,
            mappings=ADAPTER_LIFECYCLE_MAPPINGS[key],
        )

    return AdapterLifecycleReport(
        root=resolved_root,
        native_statuses=FEATURE_STATUSES,
        adapters=adapters,
        recommended_commands=_adapter_lifecycle_recommended_commands(),
    )
