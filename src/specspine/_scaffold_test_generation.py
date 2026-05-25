from __future__ import annotations

from .scaffold_generator import _generate_test_class
from .scaffold_models import (
    ScaffoldCoverageLink,
    ScaffoldSkippedCriterion,
    ScaffoldReport,
    ScaffoldTestMethod,
)
from ._scaffold_coverage_analysis import analyze_scaffold_coverage
from ._scaffold_remediation import _build_remediation_plan
from ._scaffold_report_coverage import ScaffoldCoverageContext

__all__ = [
    "build_scaffold_report",
]


def build_scaffold_report(
    ctx: ScaffoldCoverageContext,
) -> ScaffoldReport:
    methods, coverage_links, skipped_criteria, uncovered_acs = analyze_scaffold_coverage(ctx)
    slug = ctx.slug
    test_path = ctx.test_path
    class_name = ctx.class_name
    status = ctx.trace_report.status

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
