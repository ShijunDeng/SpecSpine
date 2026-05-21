from __future__ import annotations

from pathlib import Path

from .adapter_handoff_steps import (
    _adapter_handoff_recommended_commands,
    _mapping_for_status,
    _recommended_steps,
)
from .adapter_lifecycle import build_adapter_lifecycle_report
from .adapter_models import (
    ADAPTER_SPECS,
    AdapterFeatureHandoffEntry,
    AdapterFeatureHandoffReport,
)
from .features import (
    FeatureBundleNotFoundError,
    build_feature_handoff_report,
    feature_bundle_paths,
)

__all__ = [
    "build_adapter_feature_handoff_report",
]


def build_adapter_feature_handoff_report(
    root: Path,
    slug: str,
) -> AdapterFeatureHandoffReport:
    feature_report = build_feature_handoff_report(root, slug)
    resolved_root = root.expanduser().resolve()
    if not feature_report.has_native_files:
        missing_paths = tuple(feature_bundle_paths(resolved_root, slug).values())
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=missing_paths,
        )

    lifecycle_report = build_adapter_lifecycle_report(resolved_root)
    source_files = tuple(
        str(source["path"])
        for source in feature_report.sources.values()
        if source["exists"]
    )

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

    return AdapterFeatureHandoffReport(
        root=resolved_root,
        feature_id=feature_report.feature_id,
        status=feature_report.status,
        ready=feature_report.ready,
        sources=feature_report.sources,
        source_files=source_files,
        missing_files=feature_report.missing_files,
        gaps=feature_report.gaps,
        blocking_checks=feature_report.blocking_checks,
        feature_summary=feature_report.summary,
        adapters=adapters,
        recommended_commands=_adapter_handoff_recommended_commands(slug),
    )


def _replace_slug_local(commands, slug: str) -> tuple[str, ...]:
    return tuple(command.replace("<slug>", slug) for command in commands)
