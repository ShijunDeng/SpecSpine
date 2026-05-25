from __future__ import annotations

from .adapter_handoff_steps import (
    _recommended_steps,
)
from .adapter_models import (
    ADAPTER_SPECS,
    AdapterFeatureHandoffEntry,
)
from ._adapter_entry_mapping import _resolve_adapter_mapping

__all__ = [
    "_build_adapter_entries",
]


def _build_adapter_entries(
    feature_report,
    lifecycle_report,
    slug: str,
    source_files: tuple[str, ...],
) -> dict:
    adapters: dict[str, AdapterFeatureHandoffEntry] = {}
    for key in ADAPTER_SPECS:
        lifecycle_adapter = lifecycle_report.adapters[key]
        upstream_phase, upstream_artifacts, agent_focus, local_commands, notes = (
            _resolve_adapter_mapping(key, feature_report.status, slug)
        )
        adapters[key] = AdapterFeatureHandoffEntry(
            key=key,
            display_name=lifecycle_adapter.display_name,
            enabled=lifecycle_adapter.enabled,
            config=lifecycle_adapter.config,
            config_exists=lifecycle_adapter.config_exists,
            upstream_url=lifecycle_adapter.upstream_url,
            integration_surface=ADAPTER_SPECS[key].role,
            native_status=feature_report.status,
            upstream_phase=upstream_phase,
            upstream_artifacts=upstream_artifacts,
            agent_focus=agent_focus,
            local_commands=local_commands,
            recommended_upstream_steps=_recommended_steps(key, slug),
            notes=notes,
        )
    return adapters
