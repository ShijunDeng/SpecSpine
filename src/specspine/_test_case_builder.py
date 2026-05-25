from __future__ import annotations

from .feature_bundle import (
    FeatureAcceptanceTestCase,
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
)

__all__ = [
    "_acceptance_test_cases",
]


def _acceptance_test_cases(
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    test_coverage: tuple[FeatureTestCoverageLink, ...],
) -> tuple[FeatureAcceptanceTestCase, ...]:
    test_cases: list[FeatureAcceptanceTestCase] = []
    for index, criterion in enumerate(acceptance_criteria, start=1):
        coverage = tuple(
            link
            for link in test_coverage
            if link.acceptance_criterion_id == criterion.id
        )
        if any(link.done for link in coverage):
            status = "covered"
        elif coverage:
            status = "planned"
        else:
            status = "pending"
        test_cases.append(
            FeatureAcceptanceTestCase(
                id=f"TC{index:03d}",
                acceptance_criterion_id=criterion.id,
                acceptance_criterion_text=criterion.text,
                source_file=criterion.source_file,
                line=criterion.line,
                behavior=f"Pending behavior to test: {criterion.text}",
                coverage=coverage,
                status=status,
            )
        )
    return tuple(test_cases)
