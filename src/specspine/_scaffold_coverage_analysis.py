from __future__ import annotations

from .scaffold_generator import _generate_test_method
from .scaffold_models import (
    ScaffoldCoverageLink,
    ScaffoldSkippedCriterion,
)
from ._scaffold_report_coverage import ScaffoldCoverageContext

__all__ = [
    "analyze_scaffold_coverage",
]


def analyze_scaffold_coverage(
    ctx: ScaffoldCoverageContext,
) -> tuple[
    list[dict],
    list[ScaffoldCoverageLink],
    list[ScaffoldSkippedCriterion],
    list[dict[str, str]],
]:
    acceptance_criteria = ctx.trace_report.acceptance_criteria
    test_path = ctx.test_path
    class_name = ctx.class_name
    covered_acs = ctx.covered_acs
    slug = ctx.slug

    methods: list[dict] = []
    coverage_links: list[ScaffoldCoverageLink] = []
    skipped_criteria: list[ScaffoldSkippedCriterion] = []
    uncovered_acs: list[dict[str, str]] = []

    for criterion in acceptance_criteria:
        if criterion.id in covered_acs:
            skipped_criteria.append(
                ScaffoldSkippedCriterion(
                    ac_id=criterion.id,
                    reason="Already has completed test coverage link",
                )
            )
            continue
        method_info = _generate_test_method(criterion.id, criterion.text, slug)
        methods.append(method_info)
        coverage_links.append(
            ScaffoldCoverageLink(
                ac_id=criterion.id,
                target_path=test_path,
                class_name=class_name,
                method_name=method_info["method_name"],
            )
        )
        uncovered_acs.append({"ac_id": criterion.id, "ac_text": criterion.text})

    return methods, coverage_links, skipped_criteria, uncovered_acs
