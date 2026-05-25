from __future__ import annotations

from pathlib import Path

from specspine.features import get_feature_status

from specspine.archive_helpers import (
    _archive_recommended_commands,
    _archive_safety_notes,
)
from specspine.archive_models import FeatureArchiveReport

from ._archive_validators import validate_archive_inputs
from ._archive_evidence import collect_archive_evidence

__all__ = [
    "build_feature_archive_report",
]


def build_feature_archive_report(
    root: Path,
    slug: str,
    *,
    archive_id: str | None = None,
) -> FeatureArchiveReport:
    slug, resolved_root, resolved_archive_id = validate_archive_inputs(
        root, slug, archive_id
    )

    status_report = get_feature_status(resolved_root, slug)
    evidence = collect_archive_evidence(resolved_root, slug, status_report)

    return FeatureArchiveReport(
        archive_id=resolved_archive_id,
        feature_id=slug,
        workspace_root=resolved_root,
        status=status_report.status or "unknown",
        ready=evidence["ready_report"].ready,
        coverage_required=evidence["coverage_required"],
        status_report=status_report,
        ready_report=evidence["ready_report"],
        trace_report=evidence["trace_report"],
        tasks_report=evidence["tasks_report"],
        tests_report=evidence["tests_report"],
        metadata=evidence["metadata"],
        source_files=evidence["source_files"],
        missing_files=evidence["missing_files"],
        safety_notes=_archive_safety_notes(evidence["coverage_required"]),
        recommended_commands=_archive_recommended_commands(slug),
    )
