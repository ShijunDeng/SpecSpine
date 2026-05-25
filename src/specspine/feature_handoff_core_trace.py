from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureBundleNotFoundError,
    FeatureTraceReport,
    _trace_gap,
    _feature_sources_from_status,
)
from .feature_bundle_io_status_single import get_feature_status
from .feature_trace import build_feature_trace_report


def _build_trace_with_fallback(
    resolved_root: Path,
    slug: str,
    status_report,
) -> FeatureTraceReport:
    try:
        return build_feature_trace_report(resolved_root, slug)
    except FeatureBundleNotFoundError:
        missing_files = status_report.missing_files
        gaps = tuple(
            _trace_gap(
                "missing_file",
                relative_path,
                f"Missing native feature file: {relative_path}",
            )
            for relative_path in missing_files
        )
        return FeatureTraceReport(
            feature_id=slug,
            status=status_report.status or "unknown",
            sources=_feature_sources_from_status(status_report),
            missing_files=missing_files,
            acceptance_criteria=(),
            tasks=(),
            quality_checks=(),
            test_plan=(),
            gaps=gaps,
        )


__all__ = [
    "_build_trace_with_fallback",
]
