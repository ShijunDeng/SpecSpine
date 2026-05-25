from __future__ import annotations

from pathlib import Path

from .features import (
    build_feature_trace_report,
    validate_feature_slug,
)
from .scaffold_generator import (
    _existing_coverage_links,
    _generate_test_class,
    _generate_test_method,
    _slug_to_camel,
)
from .scaffold_models import (
    ScaffoldCoverageLink,
    ScaffoldRemediationStep,
    ScaffoldReport,
    ScaffoldSkippedCriterion,
    ScaffoldTestMethod,
)
from ._scaffold_remediation import _build_remediation_plan

__all__ = [
    "build_ac_test_scaffold",
]


def build_ac_test_scaffold(root: Path, slug: str) -> ScaffoldReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    trace_report = build_feature_trace_report(resolved_root, slug)
    acceptance_criteria = trace_report.acceptance_criteria
    status = trace_report.status
    covered_acs = _existing_coverage_links(resolved_root, slug)
    camel = _slug_to_camel(slug)
    class_name = f"{camel}ScaffoldTests"
    test_filename = f"test_{slug.replace('-', '_')}_scaffold.py"
    test_path = f"tests/{test_filename}"

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
