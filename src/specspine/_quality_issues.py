from __future__ import annotations

from .analysis_models import _PendingIssue
from .features import FeatureTraceChecklistItem
from ._quality_vague_terms import _vague_term_issues
from ._quality_duplicates import _duplicate_criterion_issues

__all__ = [
    "_criterion_quality_issues",
]


def _criterion_quality_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    issues.extend(_vague_term_issues(slug, acceptance_criteria))
    issues.extend(_duplicate_criterion_issues(slug, acceptance_criteria))
    return issues
