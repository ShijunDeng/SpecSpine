from __future__ import annotations

from pathlib import Path

from specspine.adapter_handoff_entries import _build_adapter_entries
from specspine.adapter_handoff_steps import (
    _adapter_handoff_recommended_commands,
)
from specspine.adapter_lifecycle import build_adapter_lifecycle_report
from specspine.adapter_models import (
    AdapterFeatureHandoffReport,
)

__all__ = [
    "assemble_adapter_feature_handoff_report",
]


def assemble_adapter_feature_handoff_report(
    feature_report,
    resolved_root: Path,
    slug: str,
) -> AdapterFeatureHandoffReport:
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
