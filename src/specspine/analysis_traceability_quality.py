from __future__ import annotations

import re

from .features import (
    FEATURE_FILE_PATHS,
    FeatureTraceChecklistItem,
)
from .analysis_models import (
    VAGUE_TERMS,
    _PendingIssue,
)
from .analysis_traceability_commands import _feature_trace_command


def _normalized_criterion_text(text: str) -> str:
    normalized = re.sub(r"`([^`]*)`", r"\1", text.lower())
    normalized = re.sub(r"\b(ac[-\s]?0*\d+|must|should|shall)\b", " ", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


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


__all__ = [
    "_normalized_criterion_text",
    "_criterion_quality_issues",
]
