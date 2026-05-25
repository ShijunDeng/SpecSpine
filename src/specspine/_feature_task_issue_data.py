from __future__ import annotations

from pathlib import Path

from .feature_bundle import FeatureMetadata, read_feature_metadata, FeatureBundleNotFoundError
from .feature_tasks_build import build_feature_tasks_report
from .feature_trace import build_feature_trace_report

__all__ = [
    "_collect_task_issue_data",
]


def _collect_task_issue_data(resolved_root: Path, slug: str) -> tuple:
    tasks_report = build_feature_tasks_report(resolved_root, slug)
    try:
        trace_report = build_feature_trace_report(resolved_root, slug)
        acceptance_criteria = trace_report.acceptance_criteria
    except FeatureBundleNotFoundError:
        acceptance_criteria = ()
    metadata: FeatureMetadata = read_feature_metadata(resolved_root, slug)
    return tasks_report, acceptance_criteria, metadata
