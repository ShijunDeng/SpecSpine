from __future__ import annotations

__all__ = [
    "serialize_tests_report",
]


def serialize_tests_report(report) -> dict[str, object]:
    return {
        "acceptance_criteria": [
            item.as_dict() for item in report.acceptance_criteria
        ],
        "blocking_checks": [
            check.as_dict() for check in report.blocking_checks
        ],
        "feature_id": report.feature_id,
        "gaps": [dict(gap) for gap in report.gaps],
        "missing_files": list(report.missing_files),
        "metadata": report.metadata.as_dict(),
        "quality_checks": [item.as_dict() for item in report.quality_checks],
        "ready": report.ready,
        "recommended_commands": list(report.recommended_commands),
        "source_files": list(report.source_files),
        "status": report.status,
        "summary": report.summary,
        "test_cases": [test_case.as_dict() for test_case in report.test_cases],
        "test_coverage": [link.as_dict() for link in report.test_coverage],
        "test_plan": [item.as_dict() for item in report.test_plan],
    }
