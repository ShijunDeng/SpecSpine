from __future__ import annotations

from .scaffold_generator import (
    _generate_test_class,
    _generate_test_method,
)
from .scaffold_models import (
    ScaffoldCoverageLink,
    ScaffoldRemediationStep,
    ScaffoldReport,
    ScaffoldSkippedCriterion,
    ScaffoldTestMethod,
)
from ._scaffold_remediation import _build_remediation_plan
from ._scaffold_report_coverage import ScaffoldCoverageContext

__all__ = [
    "assemble_scaffold_report",
]


def assemble_scaffold_report(
    ctx: ScaffoldCoverageContext,
) -> ScaffoldReport:
    acceptance_criteria = ctx.trace_report.acceptance_criteria
    status = ctx.trace_report.status
    test_path = ctx.test_path
    class_name = ctx.class_name
    covered_acs = ctx.covered_acs
    slug = ctx.slug

    methods = []
    coverage_links = []
    skipped_criteria = []
    uncovered_acs = []

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

    scaffold_source = _generate_test_class(slug, methods)
    remediation = _build_remediation_plan(slug, uncovered_acs, test_path, class_name)

    safety_notes = (
        "Scaffold generation is read-only; no subprocess or network calls made.",
        "Generated test methods contain self.fail() placeholders only.",
        "Review and implement each test method before running the scaffold file.",
    )

    return ScaffoldReport(
        feature_id=slug,
        status=status,
        scaffold_file=test_path,
        test_methods=tuple(
            ScaffoldTestMethod(
                method_name=m["method_name"],
                docstring=m["docstring"],
                ac_id=uncovered_acs[i]["ac_id"],
                ac_text=uncovered_acs[i]["ac_text"],
                body=m["body"],
            )
            for i, m in enumerate(methods)
        ),
        coverage_links=tuple(coverage_links),
        skipped_criteria=tuple(skipped_criteria),
        remediation_plan=tuple(remediation),
        safety_notes=safety_notes,
    )
