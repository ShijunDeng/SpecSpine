from __future__ import annotations

from pathlib import Path

from .feature_bundle import FeatureTestsReport, validate_feature_slug
from .feature_handoff import build_feature_handoff_report
from ._feature_tests_report_data_extractor import (
    extract_source_files,
    parse_feature_test_coverage,
)
from ._test_report_commands import _recommended_test_packet_commands
from ._test_case_builder import _acceptance_test_cases

__all__ = [
    "build_feature_tests_report",
]


def build_feature_tests_report(root: Path, slug: str) -> FeatureTestsReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    handoff = build_feature_handoff_report(resolved_root, slug)
    source_files = extract_source_files(handoff)
    test_coverage = parse_feature_test_coverage(resolved_root, slug)

    return FeatureTestsReport(
        feature_id=slug,
        status=handoff.status,
        ready=handoff.ready,
        source_files=source_files,
        missing_files=handoff.missing_files,
        gaps=handoff.gaps,
        blocking_checks=handoff.blocking_checks,
        acceptance_criteria=handoff.acceptance_criteria,
        test_plan=handoff.test_plan,
        test_coverage=test_coverage,
        test_cases=_acceptance_test_cases(
            handoff.acceptance_criteria,
            test_coverage,
        ),
        quality_checks=handoff.quality_checks,
        ready_summary=handoff.ready_summary,
        recommended_commands=_recommended_test_packet_commands(slug),
        has_native_files=handoff.has_native_files,
        metadata=handoff.metadata,
    )
