from __future__ import annotations

import json
from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    FeatureMetadata,
    FeatureTask,
    FeatureTaskIssuesReport,
    FeatureTasksReport,
    _relative_feature_paths,
    feature_bundle_paths,
    get_feature_status,
    parse_feature_tasks,
    validate_feature_slug,
)

__all__ = [
    "FeatureTasksReport",
    "build_feature_tasks_report",
]


def build_feature_tasks_report(root: Path, slug: str) -> FeatureTasksReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents: dict[str, str] = {}
    missing_files: list[str] = []
    missing_paths: list[Path] = []

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
            continue

        missing_files.append(relative_path)
        missing_paths.append(path)

    if not contents:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(missing_paths),
        )

    source_file = relative_paths["execution"]
    execution_content = contents.get("execution")
    tasks: tuple[FeatureTask, ...] = ()
    if execution_content is not None:
        tasks = parse_feature_tasks(execution_content, source_file=source_file)

    status_report = get_feature_status(resolved_root, slug)

    return FeatureTasksReport(
        feature_id=slug,
        status=status_report.status or "unknown",
        source_file=source_file,
        source_missing=execution_content is None,
        tasks=tasks,
        missing_files=tuple(missing_files),
    )
