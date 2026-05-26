from __future__ import annotations

from pathlib import Path

from ..feature_bundle import (
    FeatureTask,
    FeatureTasksReport,
    _relative_feature_paths,
    feature_bundle_paths,
    get_feature_status,
    validate_feature_slug,
)
from ._bundle_reader import _read_bundle_contents
from ._task_parser import _parse_tasks_from_content

__all__ = [
    "build_feature_tasks_report",
]


def build_feature_tasks_report(root: Path, slug: str) -> FeatureTasksReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents, missing_files = _read_bundle_contents(root, slug)

    source_file = relative_paths["execution"]
    execution_content = contents.get("execution")
    tasks = _parse_tasks_from_content(execution_content, source_file=source_file)

    status_report = get_feature_status(resolved_root, slug)

    return FeatureTasksReport(
        feature_id=slug,
        status=status_report.status or "unknown",
        source_file=source_file,
        source_missing=execution_content is None,
        tasks=tasks,
        missing_files=missing_files,
    )
