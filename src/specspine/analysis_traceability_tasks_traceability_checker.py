from __future__ import annotations

from .features import FeatureTask
from .analysis_models import (
    TEST_TARGET_RE,
    QUALITY_REFERENCE_RE,
    _PendingIssue,
)
from .analysis_traceability_commands import _feature_trace_command
from .analysis_traceability_tasks_ac_extractor import _referenced_ac_ids_for_task

__all__ = [
    "_task_traceability_issues",
]


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
