from __future__ import annotations

from ..features import FeatureTraceChecklistItem
from ..analysis_models import _PendingIssue
from ..analysis_traceability_commands import _feature_tests_command

__all__ = [
    "_detect_missing_coverage_links",
]


def _detect_missing_coverage_links(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    coverage_refs: set[str],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for criterion in acceptance_criteria:
        if criterion.id not in coverage_refs:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="medium",
                    category="coverage",
                    code="acceptance.no_coverage_link",
                    message=f"{criterion.id} has no Test Coverage link.",
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={"acceptance_criterion_id": criterion.id},
                    recommended_command=_feature_tests_command(slug),
                )
            )
    return issues
