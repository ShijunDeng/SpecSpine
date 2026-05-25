from __future__ import annotations

from pathlib import Path

from .adapter_handoff_steps import (
    _adapter_handoff_recommended_commands,
)
from .adapter_lifecycle import build_adapter_lifecycle_report
from .adapter_models import (
    AdapterFeatureHandoffReport,
)
from .features import (
    FeatureBundleNotFoundError,
    build_feature_handoff_report,
    feature_bundle_paths,
)
from .adapter_handoff_entries import _build_adapter_entries

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

    adapters = _build_adapter_entries(
        feature_report,
        lifecycle_report,
        slug,
        source_files,
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
