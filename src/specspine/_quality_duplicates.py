from __future__ import annotations

from .analysis_models import (
    _PendingIssue,
)
from .features import FeatureTraceChecklistItem
from ._quality_normalization import _normalized_criterion_text
from .analysis_traceability_commands import _feature_trace_command

__all__ = [
    "_duplicate_criterion_issues",
]


def _duplicate_criterion_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    by_text: dict[str, list[FeatureTraceChecklistItem]] = {}
    for criterion in acceptance_criteria:
        normalized = _normalized_criterion_text(criterion.text)
        if normalized:
            by_text.setdefault(normalized, []).append(criterion)

    for duplicates in by_text.values():
        if len(duplicates) < 2:
            continue
        duplicate_ids = [criterion.id for criterion in duplicates]
        for criterion in duplicates:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="low",
                    category="quality",
                    code="acceptance.duplicate_text",
                    message=(
                        f"{criterion.id} duplicates acceptance criterion text: "
                        + ", ".join(duplicate_ids)
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={
                        "acceptance_criterion_id": criterion.id,
                        "duplicate_acceptance_criterion_ids": duplicate_ids,
                    },
                    recommended_command=_feature_trace_command(slug),
                )
            )
    return issues
