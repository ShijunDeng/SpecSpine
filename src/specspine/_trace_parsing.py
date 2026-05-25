from __future__ import annotations

from .feature_bundle import (
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
    parse_acceptance_criteria,
    parse_feature_tasks,
    parse_quality_checks,
    parse_test_plan,
)

__all__ = [
    "_parse_trace_artifacts",
]


def _parse_trace_artifacts(
    contents: dict[str, str],
    spec_file: str,
    execution_file: str,
    quality_file: str,
) -> tuple[
    tuple[FeatureTraceChecklistItem, ...],
    tuple[FeatureTask, ...],
    tuple[FeatureTraceChecklistItem, ...],
    tuple[FeatureTraceTestPlanItem, ...],
]:
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...] = ()
    tasks: tuple[FeatureTask, ...] = ()
    quality_checks: tuple[FeatureTraceChecklistItem, ...] = ()
    test_plan: tuple[FeatureTraceTestPlanItem, ...] = ()

    spec_content = contents.get("spec")
    if spec_content is not None:
        acceptance_criteria = parse_acceptance_criteria(
            spec_content,
            source_file=spec_file,
        )

    execution_content = contents.get("execution")
    if execution_content is not None:
        tasks = parse_feature_tasks(execution_content, source_file=execution_file)

    quality_content = contents.get("quality")
    if quality_content is not None:
        quality_checks = parse_quality_checks(
            quality_content,
            source_file=quality_file,
        )
        test_plan = parse_test_plan(quality_content, source_file=quality_file)

    return acceptance_criteria, tasks, quality_checks, test_plan
