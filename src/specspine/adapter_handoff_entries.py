from __future__ import annotations

from .adapter_handoff_steps import (
    _mapping_for_status,
    _recommended_steps,
)
from .adapter_lifecycle import build_adapter_lifecycle_report
from .adapter_models import (
    ADAPTER_SPECS,
    AdapterFeatureHandoffEntry,
)
from .features import (
    build_feature_handoff_report,
)
from ._handoff_slug_utils import _replace_slug_local

__all__ = [
    "_build_adapter_entries",
]


def _build_adapter_entries(
    feature_report,
    lifecycle_report,
    slug: str,
    source_files: tuple[str, ...],
) -> dict:
    from .adapter_models import AdapterFeatureHandoffEntry
    adapters: dict[str, AdapterFeatureHandoffEntry] = {}
    for key in ADAPTER_SPECS:
        lifecycle_adapter = lifecycle_report.adapters[key]
        mapping = _mapping_for_status(key, feature_report.status)
        if mapping is None:
            upstream_phase = "No mapping selected"
            upstream_artifacts: tuple[str, ...] = ()
            agent_focus = (
                "Resolve the native feature status before handing work to this adapter."
            )
            local_commands: tuple[str, ...] = ()
            notes = (
                f"Native status `{feature_report.status}` has no adapter lifecycle mapping.",
                "SpecSpine did not execute upstream tools or inspect adapter runtime availability.",
            )
        else:
            upstream_phase = mapping.upstream_phase
            upstream_artifacts = mapping.upstream_artifacts
            agent_focus = mapping.agent_focus
            local_commands = _replace_slug_local(mapping.local_commands, slug)
            notes = (
                f"Selected mapping `{mapping.id}` for native status `{feature_report.status}`.",
                "Recommended upstream steps are handoff data only; SpecSpine did not execute them.",
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
