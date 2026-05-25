from __future__ import annotations

from .feature_bundle import (
    FeatureTraceChecklistItem,
    FeatureTestCoverageLink,
)

__all__ = [
    "_coverage_ready_message",
]


def _coverage_ready_message(
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...],
    test_coverage: tuple[FeatureTestCoverageLink, ...],
) -> tuple[bool, str]:
    missing_ids = []
    for criterion in acceptance_criteria:
        has_completed_local_link = any(
            link.acceptance_criterion_id == criterion.id
            and link.done
            and link.target_exists
            for link in test_coverage
        )
        if not has_completed_local_link:
            missing_ids.append(criterion.id)

    if missing_ids:
        return (
            False,
            "Missing completed local test coverage for acceptance criteria: "
            + ", ".join(missing_ids)
            + ".",
        )

    return (
        True,
        "Completed local test coverage links exist for all acceptance criteria.",
    )
