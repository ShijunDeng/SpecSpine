from __future__ import annotations

from ...features import FeatureTraceChecklistItem
from ...analysis_models import _PendingIssue
from ...analysis_traceability_commands import _feature_ready_command

__all__ = [
    "_detect_incomplete_coverage",
]


def _detect_incomplete_coverage(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    coverage_refs: set[str],
    covered_refs: set[str],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for criterion in acceptance_criteria:
        if criterion.id in coverage_refs and criterion.id not in covered_refs:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="coverage",
                    code="acceptance.no_completed_coverage",
                    message=(
                        f"{criterion.id} lacks a checked Test Coverage link to an "
                        "existing local target."
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={"acceptance_criterion_id": criterion.id},
                    recommended_command=_feature_ready_command(slug),
                )
            )
    return issues
