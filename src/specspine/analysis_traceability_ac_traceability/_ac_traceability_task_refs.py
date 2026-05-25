from __future__ import annotations

from ..features import (
    FeatureTask,
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
)
from ..analysis_models import _PendingIssue
from ..analysis_traceability_commands import (
    _feature_trace_command,
)
from ..analysis_traceability_ac_helpers import (
    _referenced_ac_ids,
)

__all__ = [
    "_ac_traceability_task_issues",
]


def _ac_traceability_task_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    tasks: tuple[FeatureTask, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    task_refs = set().union(*(_referenced_ac_ids(task.text) for task in tasks)) if tasks else set()

    for criterion in acceptance_criteria:
        if criterion.id not in task_refs:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="traceability",
                    code="acceptance.no_task_reference",
                    message=(
                        f"{criterion.id} has no execution task reference by AC id."
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={"acceptance_criterion_id": criterion.id},
                    recommended_command=_feature_trace_command(slug),
                )
            )

    return issues
