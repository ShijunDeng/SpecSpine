from __future__ import annotations

from .features import (
    FEATURE_FILE_PATHS,
    FeatureTask,
)
from .analysis_models import (
    TEST_TARGET_RE,
    QUALITY_REFERENCE_RE,
    _PendingIssue,
)
from .analysis_traceability_commands import _feature_trace_command


def _source_files(feature: dict[str, object], slug: str) -> tuple[str, ...]:
    files = feature.get("files")
    if isinstance(files, dict):
        return tuple(sorted(str(path) for path in files.values()))
    return tuple(
        relative_path.format(slug=slug)
        for relative_path in FEATURE_FILE_PATHS.values()
    )


def _missing_files(feature: dict[str, object], slug: str) -> tuple[str, ...]:
    missing = feature.get("missing_files")
    if isinstance(missing, list):
        return tuple(sorted(str(path) for path in missing))
    return tuple(
        relative_path.format(slug=slug)
        for relative_path in FEATURE_FILE_PATHS.values()
    )


def _read_test_coverage(
    root,
    slug: str,
):
    from pathlib import Path
    from .features import feature_bundle_paths, parse_test_coverage
    quality_path = feature_bundle_paths(root, slug)["quality"]
    if not quality_path.exists():
        return ()
    quality_file = FEATURE_FILE_PATHS["quality"].format(slug=slug)
    quality_content = quality_path.read_text(encoding="utf-8")
    return parse_test_coverage(
        quality_content,
        source_file=quality_file,
        root=root,
    )


def _task_traceability_issues(
    slug: str,
    tasks: tuple[FeatureTask, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for task in tasks:
        has_ac_ref = bool(_referenced_ac_ids_for_task(task.text))
        has_test_or_quality_ref = bool(
            TEST_TARGET_RE.search(task.text) or QUALITY_REFERENCE_RE.search(task.text)
        )
        if has_ac_ref or has_test_or_quality_ref:
            continue
        issues.append(
            _PendingIssue(
                feature_id=slug,
                severity="low",
                category="traceability",
                code="task.no_reference",
                message=(
                    f"{task.id} has no AC, test, or quality reference in its task text."
                ),
                source_file=task.source_file,
                line=task.line,
                evidence={"task_id": task.id},
                recommended_command=_feature_trace_command(slug),
            )
        )
    return issues


def _referenced_ac_ids_for_task(text: str) -> set[str]:
    from .analysis_models import AC_REFERENCE_RE
    return {f"AC{int(match.group(1)):03d}" for match in AC_REFERENCE_RE.finditer(text)}


__all__ = [
    "_source_files",
    "_missing_files",
    "_read_test_coverage",
    "_task_traceability_issues",
]
