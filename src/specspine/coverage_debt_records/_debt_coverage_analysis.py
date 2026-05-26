from __future__ import annotations

from ._trace_loader import _build_trace_report
from ._coverage_parser import _parse_quality_coverage
from ._gap_analyzer import _compute_coverage_gaps

__all__ = [
    "_analyze_feature_coverage_gaps",
]


def _analyze_feature_coverage_gaps(
    root,
    slug: str,
    quality_path,
    *,
    source_file: str,
) -> dict:
    trace_report = _build_trace_report(root, slug)

    test_coverage = _parse_quality_coverage(
        quality_path,
        source_file=source_file,
        root=root,
    )

    gaps = _compute_coverage_gaps(
        trace_report,
        test_coverage,
    )

    return {
        "trace_report": trace_report,
        **gaps,
        "test_coverage": test_coverage,
    }
