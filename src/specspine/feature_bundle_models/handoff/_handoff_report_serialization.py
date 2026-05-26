from __future__ import annotations

from ._handoff_report_model import FeatureHandoffReport
from ._handoff_report_summary import get_handoff_summary
from ._handoff_serializers import serialize_gaps, serialize_items

__all__ = [
    "handoff_report_as_dict",
]


def handoff_report_as_dict(report: FeatureHandoffReport) -> dict[str, object]:
    return {
        "acceptance_criteria": serialize_items(report.acceptance_criteria),
        "blocking_checks": serialize_items(report.blocking_checks),
        "feature_id": report.feature_id,
        "gaps": serialize_gaps(report.gaps),
        "missing_files": list(report.missing_files),
        "metadata": report.metadata.as_dict(),
        "next_actions": list(report.next_actions),
        "quality_checks": serialize_items(report.quality_checks),
        "ready": report.ready,
        "recommended_commands": list(report.recommended_commands),
        "release_readiness": serialize_items(report.release_readiness),
        "sources": report.sources,
        "status": report.status,
        "summary": get_handoff_summary(report),
        "tasks": serialize_items(report.tasks),
        "test_plan": serialize_items(report.test_plan),
    }
