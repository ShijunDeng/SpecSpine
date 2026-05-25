from __future__ import annotations

import re

from .analysis_models import (
    VAGUE_TERMS,
    _PendingIssue,
)
from .features import FeatureTraceChecklistItem
from ._quality_normalization import _normalized_criterion_text
from .analysis_traceability_commands import _feature_trace_command

__all__ = [
    "_criterion_quality_issues",
]


def _criterion_quality_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    by_text: dict[str, list[FeatureTraceChecklistItem]] = {}
    for criterion in acceptance_criteria:
        normalized = _normalized_criterion_text(criterion.text)
        if normalized:
            by_text.setdefault(normalized, []).append(criterion)
        lowered = criterion.text.lower()
        vague_terms = [
            term
            for term in VAGUE_TERMS
            if re.search(rf"\b{re.escape(term)}\b", lowered)
        ]
        if vague_terms:
            issues.append(
                _PendingIssue(
                    feature_id=slug,
                    severity="low",
                    category="quality",
                    code="acceptance.vague_text",
                    message=(
                        f"{criterion.id} contains vague term(s): "
                        + ", ".join(vague_terms)
                    ),
                    source_file=criterion.source_file,
                    line=criterion.line,
                    evidence={
                        "acceptance_criterion_id": criterion.id,
                        "terms": vague_terms,
                    },
                    recommended_command=_feature_trace_command(slug),
                )
            )

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
