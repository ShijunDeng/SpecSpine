from __future__ import annotations

import re

from .analysis_models import (
    VAGUE_TERMS,
    _PendingIssue,
)
from .features import FeatureTraceChecklistItem
from .analysis_traceability_commands import _feature_trace_command

__all__ = [
    "_vague_term_issues",
]


def _vague_term_issues(
    slug: str,
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for criterion in acceptance_criteria:
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
    return issues
