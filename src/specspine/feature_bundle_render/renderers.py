from __future__ import annotations

from ..feature_bundle_models import FeatureMetadata, FeatureStatusReport

__all__ = [
    "_render_metadata_lines",
    "_empty_trace_summary",
    "_feature_sources_from_status",
]


def _render_metadata_lines(metadata: FeatureMetadata) -> list[str]:
    return [
        f"- Priority: {metadata.priority}",
        f"- Owner: {metadata.owner}",
        f"- Milestone: {metadata.milestone}",
        f"- Target Release: {metadata.target_release}",
        f"- Project: {metadata.project}",
        f"- Effort: {metadata.effort}",
    ]


def _empty_trace_summary() -> dict[str, object]:
    return {
        "acceptance_criteria": {"done": 0, "open": 0, "total": 0},
        "done": 0,
        "open": 0,
        "quality_checks": {"done": 0, "open": 0, "total": 0},
        "tasks": {"done": 0, "open": 0, "total": 0},
        "test_plan": {"total": 0},
        "total": 0,
    }


def _feature_sources_from_status(
    status_report: FeatureStatusReport,
) -> dict[str, dict[str, object]]:
    return {
        kind: {
            "exists": file["exists"],
            "path": file["path"],
        }
        for kind, file in status_report.files.items()
    }
